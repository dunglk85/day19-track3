import asyncio
from app.core.database import db

async def check():
    db.connect()
    with db.driver.session() as session:
        count = session.run("MATCH (n:Chunk) RETURN count(n)").single()[0]
        print(f"Total Chunks: {count}")
        
        # Also check index
        index_result = session.run("SHOW INDEXES YIELD name, type, labelsOrTypes, properties WHERE type = 'VECTOR'").data()
        print(f"Vector Indexes: {index_result}")
    db.close()

if __name__ == "__main__":
    asyncio.run(check())
