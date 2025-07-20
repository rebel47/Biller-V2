import google.generativeai as genai
import re
from config import GOOGLE_API_KEY, GEMINI_MODEL, GENERATION_CONFIG

class BillProcessor:
    @staticmethod
    def extract_amount(text):
        # Look for amount patterns
        amount_patterns = [
            r"Total Amount: €(\d+\.?\d*)",
            r"Total: €(\d+\.?\d*)",
            r"Amount: €(\d+\.?\d*)",
            r"€(\d+\.?\d*)",
            r"(\d+\.?\d*) ?EUR",
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return 0.0

    @staticmethod
    def extract_date(text):
        # Look for date patterns
        date_patterns = [
            r"Date: (\d{4}-\d{2}-\d{2})",
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_items(text):
        items = []
        lines = text.split('\n')
        for line in lines:
            if line.startswith('-'):
                item_pattern = r"- (.*?): €(\d+\.?\d*) \(Category: (.*?)\)"
                match = re.match(item_pattern, line)
                if match:
                    item = match.group(1).strip()
                    try:
                        amount = float(match.group(2))
                        category = match.group(3).strip().lower()
                        # Only add valid items
                        if item and amount > 0 and category in ['grocery', 'utensil', 'clothing', 'miscellaneous']:
                            items.append({
                                'item': item,
                                'amount': amount,
                                'category': category
                            })
                    except ValueError:
                        continue
        return items

    @staticmethod
    def process_with_gemini(image_data, mime_type):
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            prompt = """
            Analyze this bill image and extract individual items with their prices.
            Format EACH item in EXACTLY this format:
            - Item name: €XX.XX (Category: category)
            
            Use ONLY these categories:
            - grocery (for food and drink items)
            - utensil (for household items and tools)
            - clothing (for all wearable items)
            - miscellaneous (for everything else)

            Additional guidelines:
            1. Each item MUST start with a hyphen (-)
            2. Each price MUST be in euros (€)
            3. Each category MUST be one of the four listed above
            4. Include the date if visible (Format: YYYY-MM-DD)
            """
            
            response = model.generate_content(
                [{"mime_type": mime_type, "data": image_data}, prompt],
                generation_config=GENERATION_CONFIG
            )

            extracted_text = response.text
            date = BillProcessor.extract_date(extracted_text)
            items = BillProcessor.extract_items(extracted_text)
            
            # Calculate total amount from items
            total_amount = sum(item['amount'] for item in items)
            
            return {
                'raw_text': extracted_text,
                'amount': total_amount,
                'date': date,
                'items': items
            }

        except Exception as e:
            raise Exception(f"Error processing bill with Gemini: {str(e)}")