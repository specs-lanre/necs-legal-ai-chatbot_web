from chat_client import ask_lex


def main():
    question = "What intellectual property services does NECS Legal provide?"

    result = ask_lex(question)

    print("HTTP/API TEST SUCCESS")
    print()
    print("QUESTION:")
    print(result["question"])

    print()
    print("ANSWER:")
    print(result["answer"])


if __name__ == "__main__":
    main()
