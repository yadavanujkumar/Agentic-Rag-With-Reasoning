"""
Example Usage of the Agentic GraphRAG System

This script demonstrates how to use the fraud detection agent
with various types of queries.
"""

from agent import run_agent, GOLDEN_QUERIES


def main():
    print("\n" + "="*80)
    print("AGENTIC GRAPHRAG - FRAUD DETECTION DEMO")
    print("="*80)
    
    # Check if environment is set up
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please copy .env.example to .env and add your API key")
        return
    
    if not os.getenv("NEO4J_PASSWORD"):
        print("\n❌ ERROR: NEO4J_PASSWORD not found in .env file")
        print("Please copy .env.example to .env and configure Neo4j credentials")
        return
    
    print("\n✓ Environment configured")
    print("✓ Neo4j connection ready")
    print("✓ OpenAI API key found")
    
    # Menu
    print("\n" + "="*80)
    print("SELECT A DEMO QUERY")
    print("="*80)
    
    for i, gq in enumerate(GOLDEN_QUERIES, 1):
        print(f"\n{i}. {gq['query'][:80]}...")
        print(f"   Purpose: {gq['why']}")
    
    print(f"\n{len(GOLDEN_QUERIES) + 1}. Custom query (enter your own)")
    print(f"{len(GOLDEN_QUERIES) + 2}. Exit")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(GOLDEN_QUERIES) + 2}): ").strip()
            
            # Handle empty input or explicit exit
            if not choice:
                continue
            
            if choice == str(len(GOLDEN_QUERIES) + 2):
                print("\nGoodbye!")
                break
            
            # Convert to integer
            try:
                choice_num = int(choice)
            except ValueError:
                print(f"Invalid input. Please enter a number between 1 and {len(GOLDEN_QUERIES) + 2}")
                continue
            
            if 1 <= choice_num <= len(GOLDEN_QUERIES):
                query = GOLDEN_QUERIES[choice_num - 1]['query']
                print(f"\nExecuting query {choice_num}...")
                print(f"Query: {query}\n")
                
                answer = run_agent(query, verbose=True)
                
                print("\n" + "="*80)
                print("FINAL ANSWER")
                print("="*80)
                print(answer)
                print("="*80)
            
            elif choice_num == len(GOLDEN_QUERIES) + 1:
                custom_query = input("\nEnter your question: ").strip()
                if custom_query:
                    print(f"\nExecuting custom query...")
                    answer = run_agent(custom_query, verbose=True)
                    
                    print("\n" + "="*80)
                    print("FINAL ANSWER")
                    print("="*80)
                    print(answer)
                    print("="*80)
            else:
                print(f"Invalid choice. Please enter 1-{len(GOLDEN_QUERIES) + 2}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure:")
            print("  1. Neo4j is running (docker or local)")
            print("  2. Sample data is loaded (run: python load_data.py)")
            print("  3. .env file is configured correctly")
            break
        
        # Ask if user wants to continue
        continue_choice = input("\nTry another query? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
