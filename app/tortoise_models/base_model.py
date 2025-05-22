from tortoise import fields


class BaseModel:
    id = fields.BigIntField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)


# Mysql pk 를 정할 때 주의할 점
# innodb의 특징 중 하나 -> clustering index
# pk를 기준으로 값이 비슷한 row들 끼리 디스크에서도 실제로 모여있음
# 랜덤 IO가 느리고 순차 IO가 빠름
