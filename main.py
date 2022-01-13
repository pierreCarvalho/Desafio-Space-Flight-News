
from typing import List

from sqlalchemy.sql.schema import ForeignKey
import databases
import sqlalchemy

from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine
from database import Article, Event, Launch

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi_pagination import Page, add_pagination, paginate

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "postgresql://hwdvswaagmrprv:83e2e62897e562bddf8a03215db7070237bb41c70f3c458abe7f05940bc595c5@ec2-3-89-214-80.compute-1.amazonaws.com:5432/d5078beibf8jrp"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

articles = sqlalchemy.Table(
    "articles",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("featured", sqlalchemy.Boolean),
    sqlalchemy.Column("url", sqlalchemy.String),
    sqlalchemy.Column("imageUrl", sqlalchemy.String),
    sqlalchemy.Column("newsSite", sqlalchemy.String),
    sqlalchemy.Column("summary", sqlalchemy.String),
    sqlalchemy.Column("publishedAt", sqlalchemy.String),
)

events = sqlalchemy.Table(
    "events",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("provider", sqlalchemy.String),
    sqlalchemy.Column("articleid", sqlalchemy.Integer, ForeignKey("articles.id"), nullable=False)
)

launchs = sqlalchemy.Table(
    "launchs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("provider", sqlalchemy.String),
    sqlalchemy.Column("articleid", sqlalchemy.Integer, ForeignKey("articles.id"), nullable=False)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

# Create Article Base Model

class Article(BaseModel):
    id : int
    title: str
    featured: bool
    url: str
    imageUrl: str
    newsSite: str
    summary: str
    publishedAt: str

class ArticleRequest(BaseModel):
    title: str
    featured: bool
    url: str
    imageUrl: str
    newsSite: str
    summary: str
    publishedAt: str
    events: List[dict] = []
    launches: List[dict] = []


class Event(BaseModel):
   
    id : int 
    provider : str 
    articleid : int
class Launch(BaseModel):
    
    id : int
    provider : str 
    articleid : int 


'''
# Create the database
Base.metadata.create_all(engine)
'''
# Initialize app
app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/articles/", response_model=List[Article])
async def read_articles():
    query = articles.select()
    resultado = await database.fetch_all(query)
    return resultado

@app.post("/articles/", response_model=Article)
async def create_article(article: ArticleRequest):
    query = articles.insert().values(title=article.title, featured=article.featured, url=article.url , imageUrl=article.imageUrl , newsSite=article.newsSite , summary=article.summary, publishedAt=article.publishedAt )
    last_record_id = await database.execute(query)
    if article.events:
        for event in article.events:
            _query_event = events.insert().values(id=int(event["id"]), provider=event["provider"] if event["provider"] else "", articleid=last_record_id)
            await database.execute(_query_event)
    if article.launches:
        for launch in article.launches:
            _query_launch = launchs.insert().values(id=int(launch["id"]), provider=launch["provider"] if launch["provider"] else "", articleid=last_record_id)
            await database.execute(_query_launch)
    return {**article.dict(), "id": last_record_id}


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return "Back-end Challenge 2021 🏅 - Space Flight News"

add_pagination(app) # to add all required deps to application
'''
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


add_pagination(app) # to add all required deps to application'''