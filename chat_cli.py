
from chat_client import ask_lex


def main():
    print("=" * 60)
    print("NECS LEGAL AI CHAT")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the chat.")
    print()

    while True:
        question = input("You: ").strip()

        if question.lower() in ("exit", "quit"):
            print()
            print("Lex: Goodbye.")
            break

        if not question:
            print("Lex: Please enter a question.")
            print()
            continue

        try:
            result = ask_lex(question)

            print()
            print("Lex:")
            print(result["answer"])
            print()

        except ValueError as error:
            print()
            print(f"Lex: {error}")
            print()

        except Exception as error:
            print()
            print("Lex: Sorry, I couldn't process your request.")
            print(f"Technical error: {error}")
            print()


if __name__ == "__main__":
    main()
