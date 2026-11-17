USE finditplus;

-- US-16: Secret question verification
CREATE TABLE IF NOT EXISTS item_secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL UNIQUE,
    question VARCHAR(255) NOT NULL,
    answer_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_secret_item
        FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS secret_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    user_id INT NOT NULL,
    failed_attempts INT NOT NULL DEFAULT 0,
    verified_at DATETIME NULL,
    locked_until DATETIME NULL,

    CONSTRAINT unique_item_user_secret_verification
        UNIQUE (item_id, user_id),

    CONSTRAINT fk_secret_verification_item
        FOREIGN KEY (item_id) REFERENCES items(id),

    CONSTRAINT fk_secret_verification_user
        FOREIGN KEY (user_id) REFERENCES users(id)
);

-- US-19: Anonymous communication
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    initiator_id INT NOT NULL,
    reporter_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_item_initiator_conversation
        UNIQUE (item_id, initiator_id),

    CONSTRAINT fk_conversation_item
        FOREIGN KEY (item_id) REFERENCES items(id),

    CONSTRAINT fk_conversation_initiator
        FOREIGN KEY (initiator_id) REFERENCES users(id),

    CONSTRAINT fk_conversation_reporter
        FOREIGN KEY (reporter_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    sender_id INT NOT NULL,
    body VARCHAR(1000) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_conversation
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),

    CONSTRAINT fk_message_sender
        FOREIGN KEY (sender_id) REFERENCES users(id)
);

-- US-18, US-22, US-23 need no new tables.
-- US-22 reuses items.status with the new values: archived, donated, disposed.
