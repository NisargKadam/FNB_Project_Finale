"""Main entry point for the Food & Beverage AI System"""
import logging
import json
from graph.main_graph import execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate the workflow."""
    
    print("\n" + "="*70)
    print("FOOD & BEVERAGE AI SYSTEM - WORKFLOW DEMONSTRATION")
    print("="*70 + "\n")

    # Example queries to test different workflows
    test_queries = [
        #"recipes in mexican cuisine in singapore",
        #"what cuisine would you recommend if I am mutton/chicken lover"
        #"Suggest Grilled Salmon recipe from different cuisine"
        "Suggest Zucchini Crust pizza from different cuisine"
        #"What are some vegetarian recipes I can make with chickpeas?",
        #"Tell me about the nutritional value of avocados",
       # "What items on your menu are gluten-free?",
        #"Can you recommend a dish for a romantic dinner?",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}] Query: {query}")
        print("-" * 70)
        
        try:
            response = execute_query(query)
            results.append(response)
            
            # Pretty print response
            if response.get("success"):
                print(f"Status: {response.get('status', 'UNKNOWN')}")
                print(f"Intent: {response.get('intent', 'N/A')}")
                print(f"Agents Used: {', '.join(response.get('agents_used', []))}")
                print(f"\nAnswer:\n{response.get('answer', 'N/A')}")
                if response.get('citations'):
                    print(f"\nCitations:\n{json.dumps(response['citations'], indent=2)}")
            else:
                print(f"Status: {response.get('status', 'ERROR')}")
                print(f"Reason: {response.get('reason', 'Unknown error')}")
                print(f"Message: {response.get('message', '')}")
            
            print(f"\nExecution Time: {response.get('execution_time_seconds', 0):.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"ERROR: {str(e)}")

    print("\n" + "="*70)
    print("WORKFLOW DEMONSTRATION COMPLETE")
    print("="*70 + "\n")

    # Summary statistics
    successful = sum(1 for r in results if r.get("success"))
    blocked = sum(1 for r in results if r.get("status") == "BLOCKED")
    redacted = sum(1 for r in results if r.get("status") == "REDACTED")
    
    print(f"Summary Statistics:")
    print(f"  Total Queries: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Blocked: {blocked}")
    print(f"  Redacted: {redacted}")
    print(f"  Failed: {len(results) - successful - blocked - redacted}")


if __name__ == "__main__":
    main()
