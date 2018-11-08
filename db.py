import sqlalchemy as sa

TABLE_NAME_1 = 'domains'
TABLE_NAME_2 = 'megamillions.com.ua'
metadata = sa.MetaData()


connection = {'user': 'stask', 'database': 'myproject', 'host': 'localhost', 'password': 'trololo123'}
dsn = 'postgresql://{user}:{password}@{host}/{database}'.format(**connection)
engine = sa.create_engine(dsn)
metadata.bind = engine

domains_table = sa.Table(
    TABLE_NAME_1, metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('process', sa.Boolean, default=False),
    sa.Column('ssl', sa.Boolean, default=False),
    sa.Column('domain', sa.String),
    sa.Column('pages', sa.Text),
    sa.Column('pictures', sa.Text),
    sa.Column('files', sa.Text),
    )
urls_table = sa.Table(
    TABLE_NAME_2, metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('process', sa.Boolean, default=False),
    sa.Column('url', sa.String),
    sa.Column('type', sa.String),
    sa.Column('title', sa.String),
    sa.Column('description', sa.String),
    sa.Column('text_length', sa.Integer),
    sa.Column('html_length', sa.Integer),
    sa.Column('a_links', sa.Text),
    sa.Column('all_links', sa.Text),
    )

if __name__ == '__main__':
    # metadata.drop_all()
    metadata.create_all()