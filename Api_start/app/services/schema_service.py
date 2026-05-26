from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

from app.models.schema_models import (
    TableInfo,
    ColumnInfo,
    RelationshipInfo,
    SchemaStats,
)


class SchemaService:

    @staticmethod
    async def get_tables(
        db: AsyncSession,
    ) -> list[TableInfo]:

        query = text("""
            SELECT
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = :schema_name
            ORDER BY table_name;
        """)

        result = await db.execute(
            query,
            {"schema_name": settings.db_schema},
        )

        rows = result.fetchall()

        return [
            TableInfo(
                schema_name=row.table_schema,
                table_name=row.table_name,
                table_type=row.table_type,
            )
            for row in rows
        ]

    @staticmethod
    async def get_columns(
        db: AsyncSession,
        table_name: str,
    ) -> list[ColumnInfo]:

        query = text("""
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,

                CASE
                    WHEN tc.constraint_type = 'PRIMARY KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_primary_key,

                CASE
                    WHEN fk.constraint_type = 'FOREIGN KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_foreign_key,

                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name

            FROM information_schema.columns c

            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name

            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.constraint_schema = tc.constraint_schema
                AND tc.constraint_type = 'PRIMARY KEY'

            LEFT JOIN information_schema.table_constraints fk
                ON kcu.constraint_name = fk.constraint_name
                AND kcu.constraint_schema = fk.constraint_schema
                AND fk.constraint_type = 'FOREIGN KEY'

            LEFT JOIN information_schema.constraint_column_usage ccu
                ON fk.constraint_name = ccu.constraint_name
                AND fk.constraint_schema = ccu.constraint_schema

            WHERE c.table_schema = :schema_name
            AND c.table_name = :table_name

            ORDER BY c.ordinal_position;
        """)

        result = await db.execute(
            query,
            {
                "schema_name": settings.db_schema,
                "table_name": table_name,
            },
        )

        rows = result.fetchall()

        return [
            ColumnInfo(
                schema_name=row.table_schema,
                table_name=row.table_name,

                column_name=row.column_name,
                ordinal_position=row.ordinal_position,

                data_type=row.data_type,

                is_nullable=row.is_nullable == "YES",

                default_value=row.column_default,

                max_length=row.character_maximum_length,

                numeric_precision=row.numeric_precision,
                numeric_scale=row.numeric_scale,

                is_primary_key=row.is_primary_key,
                is_foreign_key=row.is_foreign_key,

                foreign_table_name=row.foreign_table_name,
                foreign_column_name=row.foreign_column_name,
            )
            for row in rows
        ]


    @staticmethod
    async def get_relationships(db: AsyncSession) -> list[RelationshipInfo]:

        query = text("""
            SELECT
                con.conname AS constraint_name,

                nsa.nspname AS source_schema,
                rel_a.relname AS source_table,
                att_a.attname AS source_column,

                nsb.nspname AS target_schema,
                rel_b.relname AS target_table,
                att_b.attname AS target_column

            FROM pg_constraint con

            JOIN pg_class rel_a
                ON rel_a.oid = con.conrelid

            JOIN pg_namespace nsa
                ON nsa.oid = rel_a.relnamespace

            JOIN pg_class rel_b
                ON rel_b.oid = con.confrelid

            JOIN pg_namespace nsb
                ON nsb.oid = rel_b.relnamespace

            JOIN pg_attribute att_a
                ON att_a.attrelid = con.conrelid
                AND att_a.attnum = ANY(con.conkey)

            JOIN pg_attribute att_b
                ON att_b.attrelid = con.confrelid
                AND att_b.attnum = ANY(con.confkey)

            WHERE con.contype = 'f'
            AND nsa.nspname = :schema_name;
        """)

        result = await db.execute(
            query,
            {"schema_name": settings.db_schema},
        )

        rows = result.fetchall()

        return [
            RelationshipInfo(
                constraint_name=row.constraint_name,

                source_schema=row.source_schema,
                source_table=row.source_table,
                source_column=row.source_column,

                target_schema=row.target_schema,
                target_table=row.target_table,
                target_column=row.target_column,
            )
            for row in rows
        ]
    
    @staticmethod
    async def build_schema_stats(
        db: AsyncSession,
    ) -> SchemaStats:

        tables = await SchemaService.get_tables(db)

        relationships = await SchemaService.get_relationships(db)

        total_columns = 0

        for table in tables:
            columns = await SchemaService.get_columns(
                db,
                table.table_name,
            )

            total_columns += len(columns)

        return SchemaStats(
            total_tables=len(tables),
            total_columns=total_columns,
            total_relationships=len(relationships),
        )