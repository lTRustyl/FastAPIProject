-- ============================================================
-- FastAPI Project — Initial Database Setup
-- Run: docker compose exec db psql -U user -d mydb -f /app/scripts/init.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    "firstName" VARCHAR,
    "lastName" VARCHAR,
    phone VARCHAR,
    email VARCHAR UNIQUE,
    password VARCHAR NOT NULL,
    birthday TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    publication_time TIMESTAMP DEFAULT NOW(),
    status BOOLEAN DEFAULT FALSE
);

-- ── Roles ────────────────────────────────────────────────────
INSERT INTO roles (name) VALUES
    ('User'), ('Editor'), ('Administrator')
ON CONFLICT (name) DO NOTHING;

-- ── Users ────────────────────────────────────────────────────
INSERT INTO users (username, "firstName", "lastName", phone, email, password, birthday) VALUES
    ('admin',      'Admin',  'System',   '+380990000001', 'admin@example.com',         '$2b$12$tjyHO9zi/8qW0VRFZWdqTOv3YkW0lI7EER2VPgS7230hWk8de.Dqe', '1985-01-15'),
    ('editor_one', 'Emma',   'Wilson',   '+380990000002', 'emma.wilson@example.com',   '$2b$12$r.Cu3FzZKmxvh9F582n3B.4uSDJ5UPwu78xs.gyBggQdN/yUvXAiq', '1990-03-22'),
    ('editor_two', 'Liam',   'Brown',    '+380990000003', 'liam.brown@example.com',    '$2b$12$r.Cu3FzZKmxvh9F582n3B.4uSDJ5UPwu78xs.gyBggQdN/yUvXAiq', '1988-07-10'),
    ('user_one',   'Sofia',  'Davis',    '+380990000004', 'sofia.davis@example.com',   '$2b$12$93h6yhWd9tduk5DHZSeWVe5erB2yKMeFBabwSof1rWYGnJfkCZPda', '1995-11-05'),
    ('user_two',   'Noah',   'Martinez', '+380990000005', 'noah.martinez@example.com', '$2b$12$93h6yhWd9tduk5DHZSeWVe5erB2yKMeFBabwSof1rWYGnJfkCZPda', '2000-06-18'),
    ('user_three', 'Olivia', 'Taylor',   '+380990000006', 'olivia.taylor@example.com', '$2b$12$93h6yhWd9tduk5DHZSeWVe5erB2yKMeFBabwSof1rWYGnJfkCZPda', '1993-09-30')
ON CONFLICT (username) DO NOTHING;

-- ── User Roles ───────────────────────────────────────────────
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE (u.username = 'admin'      AND r.name = 'Administrator')
   OR (u.username = 'editor_one' AND r.name = 'Editor')
   OR (u.username = 'editor_two' AND r.name = 'Editor')
   OR (u.username = 'user_one'   AND r.name = 'User')
   OR (u.username = 'user_two'   AND r.name = 'User')
   OR (u.username = 'user_three' AND r.name = 'User')
ON CONFLICT DO NOTHING;

-- ── Articles ─────────────────────────────────────────────────
INSERT INTO articles (title, description, user_id, status, publication_time) VALUES
    ('Getting Started with FastAPI',       'A comprehensive guide to building APIs with FastAPI, SQLAlchemy, and Docker.',  (SELECT id FROM users WHERE username = 'editor_one'), TRUE,  '2024-01-10'),
    ('Understanding JWT Authentication',   'Deep dive into JSON Web Tokens and best practices for securing FastAPI.',       (SELECT id FROM users WHERE username = 'editor_one'), TRUE,  '2024-02-05'),
    ('SQLAlchemy Relationships Explained', 'Exploring one-to-many and many-to-many relationships in SQLAlchemy.',          (SELECT id FROM users WHERE username = 'editor_two'), TRUE,  '2024-03-15'),
    ('Docker Compose for Python Projects', 'How to containerize your FastAPI app with PostgreSQL using Docker Compose.',   (SELECT id FROM users WHERE username = 'editor_two'), FALSE, '2024-04-01'),
    ('My First Article',                   'This is my very first article on this platform about Python development.',     (SELECT id FROM users WHERE username = 'user_one'),   TRUE,  '2024-05-20'),
    ('Tips for Learning Python',           'Practical tips and resources that helped me learn Python from scratch.',       (SELECT id FROM users WHERE username = 'user_two'),   TRUE,  '2024-06-08'),
    ('Draft: API Design Patterns',         'Notes on REST API design patterns — versioning, pagination, error handling.',  (SELECT id FROM users WHERE username = 'user_three'), FALSE, '2024-07-14')
ON CONFLICT DO NOTHING;

-- ── Summary ──────────────────────────────────────────────────
SELECT 'roles'      AS table_name, COUNT(*) AS rows FROM roles
UNION ALL SELECT 'users',      COUNT(*) FROM users
UNION ALL SELECT 'user_roles', COUNT(*) FROM user_roles
UNION ALL SELECT 'articles',   COUNT(*) FROM articles;
