import os
from typing import List, Optional
import requests
import json
import databases
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.sql.schema import ForeignKey
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# SQLAlchemy specific code, as with any other app
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

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
    id: Optional[int] = None
    title: Optional[str] = None
    featured: Optional[bool] = None
    url: Optional[str] = None
    imageurl: Optional[str] = None
    newssite: Optional[str] = None
    summary: Optional[str] = None
    publishedat: Optional[str] = None
    events: List[Event] = []
    launches: List[Launch] = []


class ArticleRequestPut(BaseModel):
    title: Optional[str] = None
    featured: Optional[bool] = None
    url: Optional[str] = None
    imageurl: Optional[str] = None
    newssite: Optional[str] = None
    summary: Optional[str] = None
    publishedat: Optional[str] = None

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/articles/", response_model=List[ArticleRequest])
async def read_articles():
    query_article = (
        "SELECT article.id, article.title,article.featured,article.url,article.imageurl,article.newssite,article.summary,article.publishedat FROM articles as article "
    )
    result = await database.fetch_all(query=query_article)
    return result


@app.post("/articles/", response_model=Article)
async def create_article(article: ArticleRequest):
    query = articles.insert().values(
        title=article.title,
        featured=article.featured,
        url=article.url,
        imageurl=article.imageurl,
        newssite=article.newssite,
        summary=article.summary,
        publishedat=article.publishedat,
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


@app.get("/articles/{id}")
async def read_article(id: int):

    query = "SELECT * FROM articles WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": id})

    return result


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return "Back-end Challenge 2021 🏅 - Space Flight News"


@app.put("/articles/{id}")
async def update_article(article: ArticleRequestPut, id: int):

    try:
  
        _values = {
            "id": id,
            "title": article.title,
            "featured": article.featured,
            "url": article.url,
            "imageurl": article.imageurl,
            "newssite": article.newssite,
            "summary": article.summary,
            "publishedat": article.publishedat,
        }

        query = "UPDATE articles SET title = :title,featured = :featured,url = :url,imageurl = :imageurl,newsSite = :newssite,summary = :summary,publishedat = :publishedat WHERE id= :id "
        result = await database.fetch_one(query=query, values=_values)

        return "article update!"
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Error to update: {e} "
        )


@app.delete("/articles/{id}")
async def delete_article(id: int):
    try:
        query = "DELETE FROM articles WHERE id = :id"
        result = await database.fetch_one(query=query, values={"id": id})

        return "deleted!"
    except Exception as e:
        return "Erro: ", e

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