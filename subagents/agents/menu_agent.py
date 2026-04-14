import json
from typing import List, Dict, Any

class MenuAgent:
    """Agent to handle menu-related queries and provide Menu items and offerings"""

    def __init__(self):
        self.menu_items = self.load_menu_items()

    def load_menu_items(self, filepath: str = "data/menu_items.json") -> List[Dict[str, Any]]:
        """Load all menu items from JSON file"""
        with open(filepath, 'r') as f:
            menu_items = json.load(f)
        return menu_items

    def get_menu_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter menu items by category"""
        return [item for item in self.menu_items if item['category'].lower() == category.lower()]

    def get_available_items(self) -> List[Dict[str, Any]]:
        """Get only available menu items"""
        return [item for item in self.menu_items if item['available']]

    def get_item_by_id(self, item_id: str) -> Dict[str, Any] | None:
        """Find specific menu item by ID"""
        for item in self.menu_items:
            if item['id'] == item_id:
                return item
        return None

    def get_item_by_name(self, name: str) -> Dict[str, Any] | None:
        """Find specific menu item by exact name (case-insensitive)"""
        name_lower = name.lower()
        for item in self.menu_items:
            if item['name'].lower() == name_lower:
                return item
        return None

    def search_items_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for menu items by partial name match (case-insensitive)"""
        name_lower = name.lower()
        return [item for item in self.menu_items if name_lower in item['name'].lower()]

    def get_items_by_dietary(self, dietary_type: str) -> List[Dict[str, Any]]:
        """Get menu items by dietary preference (e.g., 'vegetarian', 'gluten-free')"""
        dietary_lower = dietary_type.lower()
        return [item for item in self.menu_items if dietary_lower in [d.lower() for d in item['dietary']]]

    def get_items_by_cuisine(self, cuisine: str) -> List[Dict[str, Any]]:
        """Get menu items by cuisine type"""
        cuisine_lower = cuisine.lower()
        return [item for item in self.menu_items if item['cuisine'].lower() == cuisine_lower]

    def get_query_type(self, user_query: str) -> str:
        """Determine the type of query from user input"""
        query_lower = user_query.lower()
        
        # Menu availability queries
        if any(word in query_lower for word in ['menu', 'available', 'what do you have', 'what items', 'offerings', 'what can i order']):
            return 'menu_list'
        
        # Price queries
        if any(word in query_lower for word in ['price', 'cost', 'how much', 'what is the price', 'what does it cost']):
            return 'price_query'
        
        # List/details queries
        if any(word in query_lower for word in ['list', 'show', 'all items', 'give me', 'details', 'information']):
            return 'detailed_list'
        
        # Default to search
        return 'search'

    def extract_item_name(self, query: str) -> str | None:
        """Extract item name from query"""
        # Remove common question words
        cleaned = query.lower()
        for word in ['price', 'cost', 'of', 'the', 'what is', 'what\'s', 'how much', 'does', 'it', 'for']:
            cleaned = cleaned.replace(word, ' ').strip()
        
        # Search for direct match
        for item in self.menu_items:
            if item['name'].lower() in cleaned:
                return item['name'].lower()
        
        return cleaned.strip() if cleaned else None

    def handle_menu_list_query(self) -> str:
        """Handle 'What is the menu available' type query"""
        available_items = self.get_available_items()
        
        if not available_items:
            return "❌ No items currently available."
        
        response = "\n" + "="*80 + "\n"
        response += "🍽️  AVAILABLE MENU ITEMS\n"
        response += "="*80 + "\n\n"
        
        # Group by category
        categories = {}
        for item in available_items:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category in sorted(categories.keys()):
            response += f"\n📂 {category}\n"
            response += "─" * 80 + "\n"
            for item in categories[category]:
                response += f"  • {item['name']:<40} ${item['price']:>6.2f} ({item['cuisine']})\n"
        
        response += "\n" + "="*80 + "\n"
        return response

    def handle_price_query(self, item_name: str) -> str:
        """Handle 'What is the price' type query"""
        if not item_name:
            return "❌ Please specify which item you'd like to know the price for."
        
        # Try to find the item
        item = self.get_item_by_name(item_name)
        if not item:
            # Try partial search
            items = self.search_items_by_name(item_name)
            if len(items) == 1:
                item = items[0]
            elif len(items) > 1:
                response = f"\n🔍 Found {len(items)} items matching '{item_name}':\n"
                response += "─" * 60 + "\n"
                for i in items:
                    response += f"  • {i['name']:<40} ${i['price']:>6.2f}\n"
                response += "─" * 60 + "\n"
                return response
            else:
                return f"❌ Item '{item_name}' not found. Try searching by different keywords."
        
        response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 PRICE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item: {item['name']}
Price: ${item['price']:.2f}
Category: {item['category']}
Availability: {'✓ Available' if item['available'] else '✗ Not Available'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return response

    def handle_detailed_list_query(self) -> str:
        """Handle 'List items with details' type query"""
        items = self.get_available_items()
        
        if not items:
            return "❌ No items available."
        
        response = "\n" + "="*100 + "\n"
        response += "📋 COMPLETE MENU WITH DETAILS\n"
        response += "="*100 + "\n\n"
        
        for idx, item in enumerate(items, 1):
            response += f"{idx}. {item['name']}\n"
            response += f"   ID: {item['id']} | Price: ${item['price']:.2f} | {item['cuisine']} | {item['category']}\n"
            response += f"   Description: {item['description']}\n"
            response += f"   Spice: {item['spice_level']} | Prep Time: {item['prep_time_minutes']} min\n"
            response += f"   Ingredients: {', '.join(item['ingredients'][:3])}{'...' if len(item['ingredients']) > 3 else ''}\n"
            response += f"   Dietary: {', '.join(item['dietary']) if item['dietary'] else 'None'}\n"
            response += "   " + "─" * 96 + "\n\n"
        
        return response

    def search_from_user_input(self, user_query: str) -> tuple[List[Dict[str, Any]], str]:
        """Search menu items based on user query"""
        query = user_query.strip().lower()
        
        # Try exact name match first
        exact_match = self.get_item_by_name(query)
        if exact_match:
            return [exact_match], self.format_item_details(exact_match)
        
        # Try partial name match
        partial_matches = self.search_items_by_name(query)
        if partial_matches:
            return partial_matches, self.format_items_list(partial_matches)
        
        # Try category match
        category_matches = self.get_menu_items_by_category(query)
        if category_matches:
            return category_matches, self.format_items_list(category_matches)
        
        # Try cuisine match
        cuisine_matches = self.get_items_by_cuisine(query)
        if cuisine_matches:
            return cuisine_matches, self.format_items_list(cuisine_matches)
        
        # Try dietary match
        dietary_matches = self.get_items_by_dietary(query)
        if dietary_matches:
            return dietary_matches, self.format_items_list(dietary_matches)
        
        return [], "❌ No items found matching your query. Try searching by name, category, cuisine, or dietary preference."

    def format_item_details(self, item: Dict[str, Any]) -> str:
        """Format a single menu item for display"""
        if not item:
            return "Item not found."
        
        details = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {item['name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price: ${item['price']:.2f}
Category: {item['category']}
Cuisine: {item['cuisine']}
Description: {item['description']}

🌶️ Spice Level: {item['spice_level']}
⏱️ Prep Time: {item['prep_time_minutes']} minutes
✓ Available: {'Yes' if item['available'] else 'No'}

🥘 Ingredients: {', '.join(item['ingredients'])}
⚠️ Allergens: {', '.join(item['allergens']) if item['allergens'] else 'None'}
🥗 Dietary: {', '.join(item['dietary']) if item['dietary'] else 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return details

    def format_items_list(self, items: List[Dict[str, Any]]) -> str:
        """Format multiple menu items for display"""
        if not items:
            return "No items found."
        
        formatted = "\n📋 Menu Items Found:\n"
        formatted += "━" * 80 + "\n"
        for item in items:
            formatted += f"{item['name']:<35} | ${item['price']:>6.2f} | {item['spice_level']}\n"
        formatted += "━" * 80 + "\n"
        return formatted
    
    def load_veg_items(self, filepath: str = "data/Veg.json") -> List[Dict[str, Any]]:
        """Load vegetarian items from Veg.json"""
        try:
            with open(filepath, 'r') as f:
                veg_items = json.load(f)
            return veg_items if isinstance(veg_items, list) else []
        except FileNotFoundError:
            return []

    def load_nonveg_items(self, filepath: str = "data/NonVeg.json") -> List[Dict[str, Any]]:
        """Load non-vegetarian items from NonVeg.json"""
        try:
            with open(filepath, 'r') as f:
                nonveg_items = json.load(f)
            return nonveg_items if isinstance(nonveg_items, list) else []
        except FileNotFoundError:
            return []

    def is_vegetarian_query(self, user_query: str) -> bool:
        """Detect if user is asking about vegetarian items"""
        query_lower = user_query.lower()
        veg_keywords = ['veg', 'vegetarian', 'veggie', 'plant-based', 'meat-free', 'no meat', 'vegetable']
        return any(keyword in query_lower for keyword in veg_keywords)

    def is_nonveg_query(self, user_query: str) -> bool:
        """Detect if user is asking about non-vegetarian items"""
        query_lower = user_query.lower()
        nonveg_keywords = ['non veg', 'non-veg', 'nonveg', 'meat', 'chicken', 'fish', 'lamb', 'beef', 'seafood', 'non vegetarian', 'mutton', 'prawns']
        return any(keyword in query_lower for keyword in nonveg_keywords)

    def handle_veg_query(self, user_query: str) -> str:
        """Handle vegetarian items query from Veg.json"""
        veg_items = self.load_veg_items()
    
        if not veg_items:
            return "❌ No vegetarian items found or file not available."
    
    # Search in veg items
        query_lower = user_query.lower()
        matching_items = []
    
        for item in veg_items:
            item_name = str(item.get('name', '')).lower()
            item_desc = str(item.get('description', '')).lower()
        # Remove veg keywords to search for actual item
            search_query = query_lower.replace('veg', '').replace('vegetarian', '').strip()
        
            if search_query and (search_query in item_name or search_query in item_desc):
                matching_items.append(item)
    
        if not matching_items:
        # Show all veg items
            response = "\n" + "="*80 + "\n"
            response += "🥗 VEGETARIAN MENU\n"
            response += "="*80 + "\n"
            response += self.format_items_list(veg_items)
            return response
    
        if len(matching_items) == 1:
            return self.format_item_details(matching_items[0])
    
        return self.format_items_list(matching_items)

    def handle_nonveg_query(self, user_query: str) -> str:
        """Handle non-vegetarian items query from NonVeg.json"""
        nonveg_items = self.load_nonveg_items()
    
        if not nonveg_items:
            return "❌ No non-vegetarian items found or file not available."
    
    # Search in nonveg items
        query_lower = user_query.lower()
        matching_items = []
    
        for item in nonveg_items:
            item_name = str(item.get('name', '')).lower()
            item_desc = str(item.get('description', '')).lower()
        # Remove non-veg keywords to search for actual item
            search_query = query_lower.replace('non veg', '').replace('non-veg', '').replace('nonveg', '').replace('meat', '').strip()
        
            if search_query and (search_query in item_name or search_query in item_desc):
                matching_items.append(item)
    
        if not matching_items:
        # Show all non-veg items
            response = "\n" + "="*80 + "\n"
            response += "🍗 NON-VEGETARIAN MENU\n"
            response += "="*80 + "\n"
            response += self.format_items_list(nonveg_items)
            return response
    
        if len(matching_items) == 1:
            return self.format_item_details(matching_items[0])
    
        return self.format_items_list(matching_items)

    def intelligent_query_handler(self, user_query: str) -> str:
        """Intelligently handle different types of user queries"""
    
    # Check for vegetarian/non-vegetarian queries first
        if self.is_nonveg_query(user_query):
            return self.handle_nonveg_query(user_query)
        
        if self.is_vegetarian_query(user_query):
            return self.handle_veg_query(user_query)
    
    # Default menu queries
        query_type = self.get_query_type(user_query)
    
        if query_type == 'menu_list':
            return self.handle_menu_list_query()
    
        elif query_type == 'price_query':
            item_name = self.extract_item_name(user_query)
            return self.handle_price_query(item_name)
    
        elif query_type == 'detailed_list':
            return self.handle_detailed_list_query()
    
        else:  # Default search
            items, response = self.search_from_user_input(user_query)
            return response


# Usage examples
if __name__ == "__main__":
    agent = MenuAgent()
    
    print("\n" + "="*60)
    print("🍽️  INTELLIGENT MENU QUERY SYSTEM")
    print("="*60)
    print("\nYou can ask:")
    print("  • 'What menu is available?'")
    print("  • 'What is the price of Paneer Tikka Masala?'")
    print("  • 'List all items with details'")
    print("  • 'Show me vegetarian items'")
    print("\nType 'quit' to exit\n")
    
    while True:
        user_query = input("🔍 Your query: ").strip()
        
        if user_query.lower() == 'quit':
            print("\nThank you! 👋\n")
            break
        
        if not user_query:
            print("⚠️  Please enter a query.\n")
            continue
        
        response = agent.intelligent_query_handler(user_query)
        print(response)