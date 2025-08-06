import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/auth_service.dart';
import '../../services/firestore_service.dart';
import '../../constants/app_theme.dart';
import '../../models/bill_model.dart';
import 'package:intl/intl.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  Map<String, dynamic>? _analytics;
  List<BillModel> _currentMonthBills = [];
  bool _isLoading = true;
  int _selectedPeriod = 0; // 0: This Month, 1: Last 3 Months, 2: Last 6 Months

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    final authService = context.read<AuthService>();
    final firestoreService = context.read<FirestoreService>();
    
    if (authService.currentUserModel != null) {
      setState(() {
        _isLoading = true;
      });

      final username = authService.currentUserModel!.username;
      
      // Load analytics data
      final analytics = await firestoreService.getSpendingAnalytics(username);
      
      // Load current month bills
      final now = DateTime.now();
      final bills = await firestoreService.getBillsForMonth(username, now);
      
      setState(() {
        _analytics = analytics;
        _currentMonthBills = bills;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: const Text('Analytics'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAnalytics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Period selector
                  _buildPeriodSelector(),
                  
                  const SizedBox(height: 24),
                  
                  // Summary cards
                  _buildSummaryCards(),
                  
                  const SizedBox(height: 32),
                  
                  // Category spending chart
                  if (_analytics?['categorySpending'] != null &&
                      (_analytics!['categorySpending'] as Map).isNotEmpty)
                    _buildCategoryChart(),
                  
                  const SizedBox(height: 32),
                  
                  // Monthly trend chart
                  if (_analytics?['monthlySpending'] != null &&
                      (_analytics!['monthlySpending'] as Map).isNotEmpty)
                    _buildMonthlyTrendChart(),
                  
                  const SizedBox(height: 32),
                  
                  // Top expenses
                  _buildTopExpenses(),
                ],
              ),
            ),
    );
  }

  Widget _buildPeriodSelector() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildPeriodTab('This Month', 0),
          ),
          Expanded(
            child: _buildPeriodTab('3 Months', 1),
          ),
          Expanded(
            child: _buildPeriodTab('6 Months', 2),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodTab(String label, int index) {
    final isSelected = _selectedPeriod == index;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedPeriod = index;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: isSelected ? Colors.white : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            fontSize: 14,
          ),
        ),
      ),
    );
  }

  Widget _buildSummaryCards() {
    final totalSpent = _analytics?['currentMonthTotal']?.toDouble() ?? 0.0;
    final billCount = _currentMonthBills.length;
    final avgBill = billCount > 0 ? totalSpent / billCount : 0.0;

    return Row(
      children: [
        Expanded(
          child: _buildSummaryCard(
            'Total Spent',
            '\$${totalSpent.toStringAsFixed(2)}',
            Icons.account_balance_wallet,
            AppColors.primary,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildSummaryCard(
            'Bills Count',
            billCount.toString(),
            Icons.receipt_long,
            AppColors.secondary,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildSummaryCard(
            'Avg. Bill',
            '\$${avgBill.toStringAsFixed(2)}',
            Icons.trending_up,
            AppColors.info,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChart() {
    final categorySpending = Map<String, double>.from(
      _analytics!['categorySpending'],
    );

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Spending by Category',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: PieChart(
              PieChartData(
                sections: categorySpending.entries.map((entry) {
                  final category = ExpenseCategory.fromString(entry.key);
                  final color = _getCategoryColor(entry.key);
                  final total = categorySpending.values.fold<double>(0.0, (a, b) => a + b);
                  final percentage = (entry.value / total) * 100;

                  return PieChartSectionData(
                    value: entry.value,
                    title: '${percentage.toStringAsFixed(1)}%',
                    color: color,
                    radius: 60,
                    titleStyle: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  );
                }).toList(),
                centerSpaceRadius: 40,
                sectionsSpace: 2,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 16,
            runSpacing: 8,
            children: categorySpending.entries.map((entry) {
              final category = ExpenseCategory.fromString(entry.key);
              final color = _getCategoryColor(entry.key);
              
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    category.displayName,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildMonthlyTrendChart() {
    final monthlySpending = Map<String, double>.from(
      _analytics!['monthlySpending'],
    );

    final sortedEntries = monthlySpending.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key));

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Monthly Spending Trend',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: const FlGridData(show: true),
                titlesData: FlTitlesData(
                  leftTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: true, reservedSize: 40),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        final index = value.toInt();
                        if (index >= 0 && index < sortedEntries.length) {
                          final monthKey = sortedEntries[index].key;
                          final parts = monthKey.split('-');
                          if (parts.length == 2) {
                            final month = int.parse(parts[1]);
                            return Text(
                              DateFormat.MMM().format(DateTime(2024, month)),
                              style: const TextStyle(fontSize: 10),
                            );
                          }
                        }
                        return const Text('');
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: true),
                lineBarsData: [
                  LineChartBarData(
                    spots: sortedEntries.asMap().entries.map((entry) {
                      return FlSpot(entry.key.toDouble(), entry.value.value);
                    }).toList(),
                    isCurved: true,
                    color: AppColors.primary,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.primary.withOpacity(0.1),
                    ),
                    dotData: const FlDotData(show: true),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopExpenses() {
    final sortedBills = List<BillModel>.from(_currentMonthBills)
      ..sort((a, b) => b.amount.compareTo(a.amount));
    final topBills = sortedBills.take(5).toList();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Top Expenses This Month',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          if (topBills.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'No expenses this month',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 16,
                  ),
                ),
              ),
            )
          else
            ...topBills.asMap().entries.map((entry) {
              final index = entry.key;
              final bill = entry.value;
              final category = ExpenseCategory.fromString(bill.category);
              
              return Padding(
                padding: EdgeInsets.only(bottom: index < topBills.length - 1 ? 16 : 0),
                child: Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: _getCategoryColor(bill.category).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(
                        child: Text(
                          category.icon,
                          style: const TextStyle(fontSize: 16),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            bill.description,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${category.displayName} • ${DateFormat('MMM dd').format(bill.date)}',
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      '\$${bill.amount.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'grocery':
        return Colors.green;
      case 'utensil':
        return Colors.orange;
      case 'clothing':
        return Colors.purple;
      case 'transport':
        return Colors.blue;
      case 'entertainment':
        return Colors.pink;
      case 'medical':
        return Colors.red;
      case 'education':
        return Colors.indigo;
      default:
        return Colors.grey;
    }
  }
}