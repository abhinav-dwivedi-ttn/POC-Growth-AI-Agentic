import asyncio
import json
import os

from dotenv import load_dotenv
from google import genai

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)


async def main():

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # -------------------------------------------------
            # 1. Get tools from MCP server
            # -------------------------------------------------

            tools_result = await session.list_tools()

            function_declarations = []

            for tool in tools_result.tools:

                function_declarations.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                })

            tools = [
                {
                    "function_declarations": function_declarations
                }
            ]

            # -------------------------------------------------
            # 2. User question
            # -------------------------------------------------

            user_question = (
                "Why hasn't the DPDP policy been assigned "
                "to employee 1024?"
            )

            print("\nUser:")
            print(user_question)

            # -------------------------------------------------
            # 3. Start conversation
            # -------------------------------------------------

            contents = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user_question
                        }
                    ]
                }
            ]

            # -------------------------------------------------
            # 4. Agent loop
            # -------------------------------------------------

            for step in range(5):

                print(f"\n--- Agent Step {step + 1} ---")

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config={
                        "system_instruction": (
                            "You are a developer support agent. "
                            "Investigate application issues using "
                            "the available tools. "
                            "Use tools whenever useful. "
                            "Do not guess when tool data is available. "
                            "Continue investigating until you have "
                            "enough information to provide a clear RCA."
                        ),
                        "tools": tools,
                    },
                )

                candidate = response.candidates[0]

                # Add Gemini response to conversation
                contents.append(candidate.content)

                tool_calls_found = False

                # -------------------------------------------------
                # 5. Process Gemini tool calls
                # -------------------------------------------------

                for part in candidate.content.parts:

                    if not part.function_call:
                        continue

                    tool_calls_found = True

                    function_call = part.function_call

                    tool_name = function_call.name

                    arguments = dict(function_call.args)

                    print(
                        f"\nAgent selected tool: {tool_name}"
                    )

                    print(
                        f"Arguments: {arguments}"
                    )

                    # -------------------------------------------------
                    # 6. Execute MCP tool
                    # -------------------------------------------------

                    result = await session.call_tool(
                        tool_name,
                        arguments
                    )

                    tool_result = []

                    for content_item in result.content:

                        if hasattr(content_item, "text"):
                            tool_result.append(
                                content_item.text
                            )

                    tool_output = "\n".join(tool_result)

                    print("\nTool result:")
                    print(tool_output)

                    # -------------------------------------------------
                    # 7. Send tool result back to Gemini
                    # -------------------------------------------------

                    contents.append(
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "function_response": {
                                        "name": tool_name,
                                        "response": {
                                            "result": tool_output
                                        }
                                    }
                                }
                            ]
                        }
                    )

                # -------------------------------------------------
                # 8. If no tool was requested,
                #    Gemini has produced the final answer
                # -------------------------------------------------

                if not tool_calls_found:

                    print("\n==============================")
                    print("FINAL RCA")
                    print("==============================")
                    print(response.text)

                    break


if __name__ == "__main__":
    asyncio.run(main())