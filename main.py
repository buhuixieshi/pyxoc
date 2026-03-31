import ollama
import asyncio
import os
import openviking as ov
from openviking.message import TextPart

class Agent:

    def __init__(self):
        # 初始化 Viking 客户端
        try:
            self.viking = ov.OpenViking(path="./viking_data")
            self.viking.initialize()

            # 创建一个唯一的会话
            self.session = self.viking.session(session_id="main_session")

            # 加载系统提示
            soul = open("system_prompt/main/SOUL.md", "r", encoding="utf-8").read()
            skill = open("system_prompt/main/SKILL.md", "r", encoding="utf-8").read()
            identity = open("system_prompt/main/IDENTITY.md", "r", encoding="utf-8").read()
            self.system_prompt = soul + skill + identity

            # 加载历史（如果有）
            print("尝试加载历史会话...")
            asyncio.run(self._load_viking_session())
        except Exception as e:
            print(f"初始化失败：{e}")
            exit()

    async def _load_viking_session(self):
        try:
            await self.session.load()  # 加载会话
            print("Viking历史会话加载成功")
        except Exception as e:
            print(f"加载历史会话失败: {e}")
            print("没有旧会话，已创建新会话")

    def get_context_sync(self, query: str):
        # 从 Viking 检索相关语义上下文
        try:
            print(f"获取与'{query}'相关的上下文...")
            ctx = asyncio.run(self.session.get_context_for_search(query=query))
            msgs = []
            for msg in ctx["current_messages"][-16:]:
                content = msg.parts[0].text.strip()
                if content:
                    msgs.append({"role": msg.role, "content": content})
            if msgs:
                msgs.insert(0, {"role":"system","content":"以下是与你的历史对话上下文："})
            return msgs
        except Exception as e:
            print(f"检索上下文时出错: {e}")
            return []

    def add_message(self, role: str, content: str):
        # 添加新消息到 Viking session
        try:
            self.session.add_message(role, [TextPart(text=content)])
        except Exception as e:
            print(f"添加消息失败: {e}")

    def chat(self, user_input, model="qwen3-vl:235b-cloud"):
        try:
            context = self.get_context_sync(user_input)
            messages = [{"role":"system","content":self.system_prompt}] + context
            messages.append({"role":"user","content":user_input})

            # 推理
            response = ollama.chat(model=model, messages=messages)
            reply = response["message"]["content"]
            print(f"AI 回复: {reply}")

            # 存储记忆
            self.add_message("user", user_input)
            self.add_message("assistant", reply)

            # 保存会话


            return reply
        except Exception as e:
            print(f"聊天过程中发生错误: {e}")
            return "出错了，请稍后再试。"



if __name__ == "__main__":
    agent = Agent()
    print("=== Agent 启动成功 ===\n")
    while True:
        i = input("你：").strip()
        if i in ["q", "quit", "exit"]:
            break
        agent.chat(i)