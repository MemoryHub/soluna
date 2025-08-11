import sys
import os
import asyncio
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.character.llm_gen import CharacterLLMGenerator
from src.character.db.character_dao import save_character

async def main():
    generator = CharacterLLMGenerator()
    try:
        # 生成一个角色
        character = await generator.generate_character(name="孙悟空", age=8, gender="男", occupation="超级赛亚人", language="Chinese")

        print(f"生成的角色: {character.name}")
        print(character.to_json())
        
        # 询问是否保存角色
        save_choice = input("是否保存此角色到MongoDB? (y/n): ")
        if save_choice.lower() == 'y':
            save_character(character)
            print("角色已保存到MongoDB!")
        else:
            print("角色未保存。")
    except Exception as e:
        print(f"生成角色时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())