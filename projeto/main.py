
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine
from database import Article, Event, Launch

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi_pagination import Page, add_pagination, paginate

# Create Article Base Model
class ArticleRequest(BaseModel):
    title: str
    featured: bool
    url: str
    imageUrl: str
    newsSite: str
    summary: str
    publishedAt: str

# Create the database
Base.metadata.create_all(engine)

# Initialize app
app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return "Back-end Challenge 2021 🏅 - Space Flight News"

@app.get("/articles/", response_model=Page[ArticleRequest])
def read_article_list():
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    articles = session.query(Article).all()

    result = []
    for article in articles:
        result.append(
            {
                "id": article.id,
                "title": article.title,
                "featured": article.featured,
                "url": article.url,
                "imageUrl": article.imageUrl,
                "newsSite": article.newsSite,
                "summary": article.summary,
                "publishedAt": article.publishedAt,
                
            }
        )
    return paginate(result)


@app.post("/article/", status_code=status.HTTP_201_CREATED)
def create_article(article: ArticleRequest):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the ToDo database model
    article_db = Article(
        title = article.title,
        featured= article.featured,
        url= article.url,
        imageUrl= article.imageUrl,
        newsSite= article.newsSite,
        summary= article.summary,
        publishedAt= article.publishedAt )

    # add it to the session and commit it
    session.add(article_db)
    session.commit()

    # grab the id given to the object from the database
    id = article_db.id

    # close the session
    session.close()

    # return the id
    return f"created todo item with id {id}"

@app.get("/article/{id}")
def read_article(id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the todo item with the given id
    article = session.query(Article).get(id)

    # close the session
    session.close()
    article_response = {
        "id": article.id,
        "title": article.title,
        "featured": article.featured,
        "url": article.url,
        "imageUrl": article.imageUrl,
        "newsSite": article.newsSite,
        "summary": article.summary,
        "publishedAt": article.publishedAt,
        
    }
    
    return article_response


@app.put("/article/{id}")
def update_article(article: ArticleRequest, id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)
    try:
        # get the article item with the given id
        article_db = session.query(Article).get(id)

        #validar campos

        # update todo item with the given task (if an item with the given id was found)
        if article_db:
            article_db.title = article.title if article.title else article_db.title
            article_db.featured = article.featured if article.featured else article_db.featured
            article_db.url = article.url if article.url else article_db.url
            article_db.imageUrl = article.imageUrl if article.imageUrl else article_db.imageUrl
            article_db.newsSite = article.newsSite if article.newsSite else article_db.newsSite
            article_db.summary = article.summary if article.summary else article_db.summary
            article_db.publishedAt = article.publishedAt if article.publishedAt else article_db.publishedAt

            session.commit()

            # close the session
            session.close()
            return "article update!"
        else:
            return "article does not exist!"
    except:
        raise HTTPException(status_code=404, detail=f"article item with id {id} not found")

@app.delete("/article/{id}")
def delete_article(id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the article item with the given id
    article = session.query(Article).get(id)

    # if todo item with given id exists, delete it from the database. Otherwise raise 404 error
    if article:
        session.delete(article)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"article with id {id} not found")


    return None


add_pagination(app) # to add all required deps to application