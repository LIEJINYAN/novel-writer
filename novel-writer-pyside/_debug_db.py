import sys
sys.path.insert(0, '.')

from models import db_manager, Project, Volume, Chapter

db_manager.init_db()

session = db_manager.get_session()
try:
    projects = session.query(Project).all()
    print('=== 所有项目 ===')
    for p in projects:
        print(f'ID: {p.id}, 名称: {p.name}, writing_method: "{p.writing_method}", target_words: {p.target_words}')
        volumes = session.query(Volume).filter_by(project_id=p.id, is_deleted=False).all()
        print(f'  分卷数: {len(volumes)}')
        for v in volumes:
            chapters = session.query(Chapter).filter_by(volume_id=v.id, is_deleted=False).all()
            print(f'    分卷{v.id}: {v.name}, 章节数: {len(chapters)}')
            for c in chapters:
                print(f'      章节{c.chapter_number}: {c.title}, 字数: {c.word_count}')
finally:
    session.close()
