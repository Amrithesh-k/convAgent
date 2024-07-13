from agent import SalesReportAgent

def main():
    agent = SalesReportAgent()
    print("Welcome to the Sales Report Assistant!")

    while True:
        user_input = input("You: ")
        if user_input:
            print("AI is thinking")
    
        if user_input.lower() == 'exit':
            print("AI: Thank you for using the Sales Report Assistant. Goodbye!")
            break
        response = agent.process_input(user_input)
        print("AI:", response)

if __name__ == "__main__":
    main()