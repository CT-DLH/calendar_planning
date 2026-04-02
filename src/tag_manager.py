
from src.storage import Storage

class Tag:
    def __init__(self, id, name, color=None, is_builtin=False):
        self.id = id
        self.name = name
        self.color = color
        self.is_builtin = is_builtin

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "is_builtin": self.is_builtin
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color"),
            is_builtin=data.get("is_builtin", False)
        )


class TagManager:
    BUILTIN_TAGS = [
        {"id": "normal", "name": "一般", "color": "#9ca3af", "is_builtin": True},
        {"id": "important", "name": "重要", "color": "#f59e0b", "is_builtin": True},
        {"id": "urgent", "name": "紧急", "color": "#ef4444", "is_builtin": True},
        {"id": "important_urgent", "name": "重要且紧急", "color": "#8b5cf6", "is_builtin": True}
    ]

    def __init__(self):
        self.tags = []
        self.load_tags()

    def load_tags(self):
        saved_tags = Storage.load("tags", [])
        self.tags = [Tag.from_dict(tag_data) for tag_data in saved_tags]
        
        for builtin_tag in self.BUILTIN_TAGS:
            if not any(tag.id == builtin_tag["id"] for tag in self.tags):
                self.tags.append(Tag(**builtin_tag))
        
        self._sort_tags()

    def save_tags(self):
        tag_dicts = [tag.to_dict() for tag in self.tags]
        Storage.save("tags", tag_dicts)

    def _sort_tags(self):
        self.tags.sort(key=lambda tag: (tag.is_builtin, tag.id))

    def get_all_tags(self):
        return self.tags

    def get_tag_by_id(self, tag_id):
        for tag in self.tags:
            if tag.id == tag_id:
                return tag
        return None

    def get_tag_by_name(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag
        return None

    def create_tag(self, name, color=None):
        if not name or not name.strip():
            raise ValueError("标签名称不能为空")
        
        if self.get_tag_by_name(name.strip()):
            raise ValueError("标签名称已存在")
        
        tag_id = f"custom_{len([t for t in self.tags if not t.is_builtin]) + 1}"
        new_tag = Tag(id=tag_id, name=name.strip(), color=color, is_builtin=False)
        self.tags.append(new_tag)
        self._sort_tags()
        self.save_tags()
        return new_tag

    def update_tag(self, tag_id, new_name=None, new_color=None):
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("标签不存在")
        
        if tag.is_builtin:
            raise ValueError("不能编辑内置标签")
        
        if new_name:
            existing_tag = self.get_tag_by_name(new_name.strip())
            if existing_tag and existing_tag.id != tag_id:
                raise ValueError("标签名称已存在")
            tag.name = new_name.strip()
        
        if new_color is not None:
            tag.color = new_color
        
        self.save_tags()
        return tag

    def delete_tag(self, tag_id):
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("标签不存在")
        
        if tag.is_builtin:
            raise ValueError("不能删除内置标签")
        
        self.tags = [t for t in self.tags if t.id != tag_id]
        self.save_tags()
        return True

    def get_builtin_tags(self):
        return [tag for tag in self.tags if tag.is_builtin]

    def get_custom_tags(self):
        return [tag for tag in self.tags if not tag.is_builtin]
