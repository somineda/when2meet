import string
from typing import Final  # 재할당을 막아줌

# 결과 값에 들어갈 수 있는 문자, 숫자를 미리 지정
# 이 값들의 개수가 64개면 base64 가 되고, 62개면 base62


class Base62:
    BASE: Final[str] = string.ascii_letters + string.digits
    BASE_LEN: Final[int] = len(BASE)

    @classmethod
    def encode(cls, num: int) -> str:
        if num < 0:
            raise ValueError(f"{cls}.encode() needs positive integer but you passed: {num}")

        if num == 0:
            return cls.BASE[0]

        result = []
        while num:
            num, remainder = divmod(num, cls.BASE_LEN)
            result.append(cls.BASE[remainder])
        return "".join(result)
