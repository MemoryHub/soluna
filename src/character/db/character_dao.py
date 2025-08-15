from src.db.mongo_client import mongo_client
from src.character.model.character import Character

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
            Character: 角色对象
        """
        try:
            character_dict = self.characters_collection.find_one({'character_id': character_id})
            if character_dict:
                # 移除MongoDB自动添加的_id字段
                character_dict.pop('_id', None)
                # 从字典创建Character对象
                return Character(**character_dict)
            return None
        except Exception as e:
            print(f"获取角色失败: {e}")
            raise

    def get_all_characters(self):
        """获取所有角色

        Returns:
            list: 角色列表
        """
        try:
            characters = list(self.characters_collection.find())
            # 移除每个角色的_id字段
            for character in characters:
                character.pop('_id', None)
            return characters
        except Exception as e:
            print(f"获取所有角色失败: {e}")
            raise

    def delete_character(self, character_id):
        """根据ID删除角色

        Args:
            character_id: 角色ID

        Returns:
            bool: 是否删除成功
        """
        try:
            result = self.characters_collection.delete_one({'character_id': character_id})
            print(f"删除角色成功: {character_id}")
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除角色失败: {e}")
            return False

# 创建DAO实例
dao = CharacterDAO()

def save_character(character):
    """保存角色的便捷函数"""
    return dao.save_character(character)

def get_all_characters():
    """获取所有角色的便捷函数"""
    return dao.get_all_characters()


def get_character_by_id(character_id):
    """根据ID获取角色的便捷函数"""
    return dao.get_character_by_id(character_id)

def delete_character(character_id):
    """删除角色的便捷函数"""
    return dao.delete_character(character_id)