from agent.controller import run_agent

print("Friday is online.")
print("Type 'friday stop' to shutdown.\n")

while True:

    user_input = input("You: ")

    if user_input.lower() in ["friday stop", "exit"]:
        print("Friday: Shutting down.")
        break

    response = run_agent(user_input)

    if response:
        print("\nFriday:", response)
        print()