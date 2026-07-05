from app.services.ws import WSService

async def notify_new_comment(
        article_id: int,
        comment_id: int,
        commenter: str,
        content: str,
        author_id: int,
):
    await WSService.notify_new_comment(
        article_id=article_id,
        comment_id=comment_id,
        commenter=commenter,
        content=content,
        author_id=author_id,
    )

async def notify_new_article(
        article_id: int, 
        title: str, 
        author: str
):
    await WSService.notify_new_article(
        article_id=article_id,
        title=title,
        author=author,
    )