from src.db.mongo_client import mongo_client

class CharacterDAO:
    def __init__(self):
        # 获取数据库连接
        self.db = mongo_client.get_database()
        # 获取角色集合
        self.characters_collection = self.db['characters']

    def save_character(self, character):
        """保存角色到MongoDB

        Args:
            character: 角色对象

        Returns:
            str: 保存后的角色ID
        """
        try:
            # 将角色对象转换为字典
            character_dict = character.to_dict() if hasattr(character, 'to_dict') else character.__dict__

            # 检查是否已存在此角色
            existing_character = self.characters_collection.find_one({'character_id': character_dict.get('character_id')})

            if existing_character:
                # 更新现有角色
                result = self.characters_collection.update_one(
                    {'character_id': character_dict.get('character_id')},
                    {'$set': character_dict}
                )
                print(f"更新角色成功: {character_dict.get('name')}")
                return character_dict.get('character_id')
            else:
                # 插入新角色
                result = self.characters_collection.insert_one(character_dict)
                print(f"插入角色成功: {character_dict.get('name')}")
                return character_dict.get('character_id')
        except Exception as e:
            print(f"保存角色失败: {e}")
            raise

    def get_character_by_id(self, character_id):
        """根据ID获取角色

        Args:
            character_id: 角色ID

        Returns:
            dict: 角色数据
        """
        try:
            return self.characters_collection.find_one({'character_id': character_id})
        except Exception as e:
            print(f"获取角色失败: {e}")
            raise

    def get_all_characters(self):
        """获取所有角色

        Returns:
            list: 角色列表
        """
        try:
            return list(self.characters_collection.find())
        except Exception as e:
            print(f"获取所有角色失败: {e}")
            raise

# 创建DAO实例
dao = CharacterDAO()

def save_character(character):
    """保存角色的便捷函数"""
    return dao.save_character(character)