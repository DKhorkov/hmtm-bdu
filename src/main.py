import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

books = [
    {
        "id": 1,
        "name": "Python",
        "author": "Mathey"
    },
    {
        "id": 2,
        "name": "Java",
        "author": "John"
    }
]


@app.get("/books",
         tags=["Книги 📚"],
         summary="Список книг"
         )
def get_books():
    return books


@app.get("/books/{book_id}",
         tags=["Книги 📚"],
         summary="GET-Ручка получения книги"
         )
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


class NewBook(BaseModel):
    name: str
    author: str


@app.post("/books",
          tags=["Книги 📚"],
          summary="POST-Ручка добавления книги"
          )
def add_book(book: NewBook):
    books.append({
        "id": len(books) + 1,  # Пример без БД
        "name": book.name,
        "author": book.author
    })
    return {
        "success": True,
        "message": "Книга успешно добавлена"
    }  # Просто показываем пользователю, что все OK


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)
