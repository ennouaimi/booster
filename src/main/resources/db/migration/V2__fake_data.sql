-- =====================
-- Insert users
-- =====================
INSERT INTO users (username, password) VALUES
('alice', '$2a$10$7XHIM9GMwiHzUI/fpFJ/Fejv91MK4L0ierSK4jdK5JXNK0DQw0QZC'),
('bob', '$2a$10$7XHIM9GMwiHzUI/fpFJ/Fejv91MK4L0ierSK4jdK5JXNK0DQw0QZC'),
('charlie', '$2a$10$7XHIM9GMwiHzUI/fpFJ/Fejv91MK4L0ierSK4jdK5JXNK0DQw0QZC');

-- Reset  sequence
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM users), false);
