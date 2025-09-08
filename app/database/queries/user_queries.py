from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.database import User
from app.core.database import SessionLocal
from passlib.context import CryptContext
import re

# 비밀번호 해싱을 위한 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserQueries:
    """사용자 관련 데이터베이스 쿼리 클래스"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호를 검증합니다."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """비밀번호를 해싱합니다."""
        return pwd_context.hash(password)
    
    def validate_email(self, email: str) -> bool:
        """이메일 형식을 검증합니다."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> bool:
        """비밀번호 강도를 검증합니다."""
        # 최소 8자, 영문, 숫자 포함
        if len(password) < 8:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    # 사용자 CRUD 작업
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자를 조회합니다 (페이지네이션)."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, email: str, password: str, name: str) -> Optional[User]:
        """새로운 사용자를 생성합니다."""
        # 이메일 형식 검증
        if not self.validate_email(email):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        
        # 비밀번호 강도 검증
        if not self.validate_password(password):
            raise ValueError("비밀번호는 최소 8자 이상이며 영문과 숫자를 포함해야 합니다.")
        
        # 이메일 중복 검사
        if self.get_user_by_email(email):
            raise ValueError("이미 등록된 이메일입니다.")
        
        try:
            hashed_password = self.get_password_hash(password)
            user = User(
                email=email,
                name=name,
                password_hash=hashed_password
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("사용자 생성 중 오류가 발생했습니다.")
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """사용자 정보를 업데이트합니다."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # 이메일 변경 시 중복 검사
        if 'email' in kwargs and kwargs['email'] != user.email:
            if not self.validate_email(kwargs['email']):
                raise ValueError("올바른 이메일 형식이 아닙니다.")
            if self.get_user_by_email(kwargs['email']):
                raise ValueError("이미 등록된 이메일입니다.")
        
        # 비밀번호 변경 시 해싱
        if 'password' in kwargs:
            if not self.validate_password(kwargs['password']):
                raise ValueError("비밀번호는 최소 8자 이상이며 영문과 숫자를 포함해야 합니다.")
            kwargs['password_hash'] = self.get_password_hash(kwargs['password'])
            del kwargs['password']
        
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("사용자 정보 업데이트 중 오류가 발생했습니다.")
    
    def delete_user(self, user_id: str) -> bool:
        """사용자를 삭제합니다."""
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """사용자 인증을 수행합니다."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """사용자 비밀번호를 변경합니다."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 기존 비밀번호 검증
        if not self.verify_password(old_password, user.password_hash):
            raise ValueError("기존 비밀번호가 올바르지 않습니다.")
        
        # 새 비밀번호 강도 검증
        if not self.validate_password(new_password):
            raise ValueError("비밀번호는 최소 8자 이상이며 영문과 숫자를 포함해야 합니다.")
        
        # 비밀번호 업데이트
        user.password_hash = self.get_password_hash(new_password)
        self.db.commit()
        return True
    
    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자를 검색합니다 (이름 또는 이메일)."""
        return self.db.query(User).filter(
            (User.name.contains(query)) | (User.email.contains(query))
        ).offset(skip).limit(limit).all()
    
    def get_user_count(self) -> int:
        """전체 사용자 수를 조회합니다."""
        return self.db.query(User).count()
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if self.db:
            self.db.close()
