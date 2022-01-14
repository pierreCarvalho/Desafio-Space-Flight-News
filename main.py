from tkinter import W
from typing import List, Optional
import requests
import json

from sqlalchemy.sql.schema import ForeignKey
import databases
import sqlalchemy
from sqlalchemy.sql.expression import Select
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
    sqlalchemy.Column("imageurl", sqlalchemy.String),
    sqlalchemy.Column("newssite", sqlalchemy.String),
    sqlalchemy.Column("summary", sqlalchemy.String),
    sqlalchemy.Column("publishedat", sqlalchemy.String),
)

events = sqlalchemy.Table(
    "events",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("provider", sqlalchemy.String),
    sqlalchemy.Column(
        "articleid",
        sqlalchemy.Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

launchs = sqlalchemy.Table(
    "launchs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_launch", sqlalchemy.String),
    sqlalchemy.Column("provider", sqlalchemy.String),
    sqlalchemy.Column(
        "articleid",
        sqlalchemy.Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

# Create Article Base Model


class Article(BaseModel):
    id: int
    title: Optional[str] = None
    featured: Optional[bool] = None
    url: Optional[str] = None
    imageurl: Optional[str] = None
    newssite: Optional[str] = None
    summary: Optional[str] = None
    publishedat: Optional[str] = None


class Event(BaseModel):

    id: int
    provider: str
    articleid: int


class Launch(BaseModel):

    id: int
    id_launch: str
    provider: str
    articleid: int


class ArticleRequest(BaseModel):
    title: Optional[str] = None
    featured: Optional[bool] = None
    url: Optional[str] = None
    imageurl: Optional[str] = None
    newssite: Optional[str] = None
    summary: Optional[str] = None
    publishedat: Optional[str] = None
    events: List[Event] = []
    launches: List[Launch] = []


# Initialize app
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/articles/", response_model=List[ArticleRequest])
async def read_articles():
    # query = articles.select()
    # resultado = await database.fetch_all(query)
    # query = (
    #    "SELECT *  FROM articles inner join events on events.articleid = articles.id "
    # )

    # query_launch = "SELECT launch.id_launch, launch.provider, launch.articleid from launchs as launch"
    query_article = (
        "SELECT article.id, article.title,article.featured FROM articles as article "
    )
    result = await database.fetch_all(query=query_article)
    """_query = "SELECT *  FROM events"
    _result = await database.fetch_all(query=query_launch)
    print(result)
    print(_result)
    launhcs = []
    for j in _result:
        launhcs.append(
            {
                "id_launch": j["id_launch"],
                "provider": j["provider"],
                "articleid": j["articleid"],
            }
        )
    for i in result:
        print(i)
        print(i["title"])
        i["launches"] = []
        for k in launhcs:
            if k["articleid"] == i["id"]:
                print("ENCONTREI")
                i["launches"].append({"id": k["id_launch"], "provider": k["provider"]})"""
    return result


@app.post("/articles/", response_model=Article)
async def create_article(article: ArticleRequest):
    query = articles.insert().values(
        title=article.title,
        featured=article.featured,
        url=article.url,
        imageUrl=article.imageUrl,
        newsSite=article.newsSite,
        summary=article.summary,
        publishedAt=article.publishedAt,
    )
    last_record_id = await database.execute(query)
    if article.events:
        for event in article.events:
            _query_event = events.insert().values(
                id=event["id"],
                provider=event["provider"] if event["provider"] else "",
                articleid=last_record_id,
            )
            await database.execute(_query_event)
    if article.launches:
        for launch in article.launches:
            _query_launch = launchs.insert().values(
                id_launch=launch["id"],
                provider=launch["provider"] if launch["provider"] else "",
                articleid=last_record_id,
            )
            await database.execute(_query_launch)
    return {**article.dict(), "id": last_record_id}


@app.get("/article/{id}")
async def read_article(id: int):

    query = "SELECT * FROM articles WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": id})

    return result


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return "Back-end Challenge 2021 🏅 - Space Flight News"


@app.put("/article/{id}")
async def update_article(article: ArticleRequest, id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)
    try:
        # get the article item with the given id
        # create a new database session

        # update todo item with the given task (if an item with the given id was found)
        if article:

            _values = {
                "id": id,
                "title": article.title,
                "featured": article.featured,
                "url": article.url,
                "imageUrl": article.imageUrl,
                "newsSite": article.newsSite,
                "summary": article.summary,
                "publishedAt": article.publishedAt,
            }

            query = "UPDATE articles SET title = :title,featured = :featured,url = :url,imageUrl = :imageUrl,newsSite = :newsSite,summary = :summary,publishedAt = :publishedAt, WHERE id= :id "
            result = await database.fetch_one(query=query, values=_values)

            return "article update!"
        else:
            return "article does not exist!"
    except:
        raise HTTPException(
            status_code=404, detail=f"article item with id {id} not found"
        )


@app.delete("/article/{id}")
async def delete_article(id: int):
    # create a new database session
    query = "DELETE FROM articles WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": id})

    return None


@app.get("/buscar-dados/")
async def buscar_dados():

    request = requests.get("https://api.spaceflightnewsapi.net/v3/articles/")
    artigos = json.loads(request.content)
    for artigo in artigos:
        query = articles.insert().values(
            title=artigo["title"],
            featured=artigo["featured"],
            url=artigo["url"],
            imageurl=artigo["imageUrl"],
            newssite=artigo["newsSite"],
            summary=artigo["summary"],
            publishedat=artigo["publishedAt"],
        )
        last_record_id = await database.execute(query)
        if artigo["events"]:
            for event in artigo["events"]:
                _query_event = events.insert().values(
                    id=event["id"],
                    provider=event["provider"] if event["provider"] else "",
                    articleid=last_record_id,
                )
                await database.execute(_query_event)
        if artigo["launches"]:
            for launch in artigo["launches"]:
                _query_launch = launchs.insert().values(
                    id_launch=launch["id"],
                    provider=launch["provider"] if launch["provider"] else "",
                    articleid=last_record_id,
                )
                await database.execute(_query_launch)