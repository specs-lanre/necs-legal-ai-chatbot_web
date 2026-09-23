import requests


API_URL = "http://127.0.0.1:8000/chat"


def main():
    question = "What intellectual property services does NECS Legal provide?"

    response = requests.post(
        API_URL,
        json={"question": question},
        timeout=60,
    )

    print("HTTP STATUS:", response.status_code)
    print()
    print("RAW RESPONSE:")
    print(response.text)

    response.raise_for_status()

    data = response.json()

    print()
    print("QUESTION:")
    print(data["question"])

    print()
    print("ANSWER:")
    print(data["answer"])


if __name__ == "__main__":
    main()
