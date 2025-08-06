import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_service.dart';
import '../../services/firestore_service.dart';
import '../../constants/app_theme.dart';
import '../../models/bill_model.dart';
import '../../widgets/bill_list_item.dart';
import '../../widgets/filter_chip_widget.dart';
import 'package:intl/intl.dart';

class MyBillsScreen extends StatefulWidget {
  const MyBillsScreen({super.key});

  @override
  State<MyBillsScreen> createState() => _MyBillsScreenState();
}

class _MyBillsScreenState extends State<MyBillsScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String? _selectedCategory;
  DateTime? _selectedMonth;
  List<BillModel> _filteredBills = [];
  bool _isSelectionMode = false;
  final Set<String> _selectedBillIds = {};

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _filterBills(List<BillModel> bills) {
    setState(() {
      _filteredBills = bills.where((bill) {
        bool matchesSearch = _searchQuery.isEmpty ||
            bill.description.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            bill.category.toLowerCase().contains(_searchQuery.toLowerCase());
        
        bool matchesCategory = _selectedCategory == null ||
            bill.category == _selectedCategory;
        
        bool matchesMonth = _selectedMonth == null ||
            (bill.date.year == _selectedMonth!.year &&
             bill.date.month == _selectedMonth!.month);
        
        return matchesSearch && matchesCategory && matchesMonth;
      }).toList();
    });
  }

  void _clearFilters() {
    setState(() {
      _searchQuery = '';
      _selectedCategory = null;
      _selectedMonth = null;
      _searchController.clear();
    });
  }

  void _toggleSelectionMode() {
    setState(() {
      _isSelectionMode = !_isSelectionMode;
      if (!_isSelectionMode) {
        _selectedBillIds.clear();
      }
    });
  }

  void _toggleBillSelection(String billId) {
    setState(() {
      if (_selectedBillIds.contains(billId)) {
        _selectedBillIds.remove(billId);
      } else {
        _selectedBillIds.add(billId);
      }
    });
  }

  Future<void> _deleteSelectedBills() async {
    if (_selectedBillIds.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Bills'),
        content: Text(
          'Are you sure you want to delete ${_selectedBillIds.length} bill(s)? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final firestoreService = context.read<FirestoreService>();
      final success = await firestoreService.deleteBills(_selectedBillIds.toList());
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bills deleted successfully'),
            backgroundColor: AppColors.success,
          ),
        );
        _toggleSelectionMode();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to delete bills'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();
    
    if (authService.currentUserModel == null) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: Text(_isSelectionMode ? '${_selectedBillIds.length} selected' : 'My Bills'),
        centerTitle: !_isSelectionMode,
        leading: _isSelectionMode
            ? IconButton(
                icon: const Icon(Icons.close),
                onPressed: _toggleSelectionMode,
              )
            : null,
        actions: [
          if (_isSelectionMode) ...[
            if (_selectedBillIds.isNotEmpty)
              IconButton(
                icon: const Icon(Icons.delete, color: AppColors.error),
                onPressed: _deleteSelectedBills,
              ),
          ] else ...[
            IconButton(
              icon: const Icon(Icons.select_all),
              onPressed: _toggleSelectionMode,
            ),
            PopupMenuButton<String>(
              onSelected: (value) {
                if (value == 'clear_filters') {
                  _clearFilters();
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'clear_filters',
                  child: Row(
                    children: [
                      Icon(Icons.clear_all, size: 20),
                      SizedBox(width: 8),
                      Text('Clear Filters'),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
      body: Column(
        children: [
          // Search and Filters
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Column(
              children: [
                // Search bar
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Search bills...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              setState(() {
                                _searchQuery = '';
                              });
                            },
                          )
                        : null,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.borderLight),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.borderLight),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: AppColors.primary, width: 2),
                    ),
                    filled: true,
                    fillColor: Colors.grey.withOpacity(0.1),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  onChanged: (value) {
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
                
                const SizedBox(height: 16),
                
                // Filter chips
                SizedBox(
                  height: 40,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    children: [
                      FilterChipWidget(
                        label: 'All Categories',
                        isSelected: _selectedCategory == null,
                        onTap: () {
                          setState(() {
                            _selectedCategory = null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      ...ExpenseCategory.values.map((category) =>
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: FilterChipWidget(
                            label: category.displayName,
                            icon: category.icon,
                            isSelected: _selectedCategory == category.value,
                            onTap: () {
                              setState(() {
                                _selectedCategory = _selectedCategory == category.value
                                    ? null
                                    : category.value;
                              });
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Bills list
          Expanded(
            child: StreamBuilder<List<BillModel>>(
              stream: context.read<FirestoreService>().getBillsStream(
                authService.currentUserModel!.username,
              ),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (snapshot.hasError) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 64,
                          color: AppColors.error,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Error loading bills',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          snapshot.error.toString(),
                          style: Theme.of(context).textTheme.bodyMedium,
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () => setState(() {}),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }

                final bills = snapshot.data ?? [];
                _filterBills(bills);

                if (_filteredBills.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          bills.isEmpty ? Icons.receipt_outlined : Icons.search_off,
                          size: 64,
                          color: AppColors.textSecondary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          bills.isEmpty ? 'No bills yet' : 'No bills match your filters',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          bills.isEmpty
                              ? 'Start by uploading your first bill!'
                              : 'Try adjusting your search or filters',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        if (bills.isEmpty) ...[
                          const SizedBox(height: 24),
                          ElevatedButton.icon(
                            onPressed: () {
                              // Navigate to upload screen
                            },
                            icon: const Icon(Icons.add),
                            label: const Text('Upload Bill'),
                          ),
                        ],
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: _filteredBills.length,
                  itemBuilder: (context, index) {
                    final bill = _filteredBills[index];
                    return BillListItem(
                      bill: bill,
                      isSelectionMode: _isSelectionMode,
                      isSelected: _selectedBillIds.contains(bill.id),
                      onTap: _isSelectionMode
                          ? () => _toggleBillSelection(bill.id)
                          : () {
                              // Navigate to bill details
                            },
                      onLongPress: () {
                        if (!_isSelectionMode) {
                          _toggleSelectionMode();
                        }
                        _toggleBillSelection(bill.id);
                      },
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}