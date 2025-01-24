from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем базовый класс для моделей
Base = declarative_base()

# Определение модели User 
class User(Base): 
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    age = Column(Integer)    
    def __repr__(self):
        return f"<User (name='{self.name}', age={self.age})>"

# Создание двигателя подключения к базе данных SQLite 
engine = create_engine('sqlite:///example.db', echo=False)

# Создание всех таблиц
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Добавление нового пользователя 
new_user = User(name='Алекс', age=30) 
session.add(new_user)
session.commit()
# Запрос пользователей
users = session.query(User).all()
for user in users: 
    print(user)

def add_user_orm(name, age):
    """Добавление пользователя с использованием ORM."""
    new_user = User (name=name, age=age)
    session.add(new_user)
    try:
        session.commit()
        print(f"Пользователь '{name}' добавлен (ORM).")
    except IntegrityError:
        session.rollback()
        print(f"Пользователь '{name}' уже существует (ORM).")

