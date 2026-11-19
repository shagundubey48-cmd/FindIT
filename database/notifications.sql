USE finditplus;

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    matched_item_id INT NOT NULL,
    message VARCHAR(300) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT fk_notification_item
        FOREIGN KEY (item_id) REFERENCES items(id),

    CONSTRAINT fk_notification_matched_item
        FOREIGN KEY (matched_item_id) REFERENCES items(id),

    CONSTRAINT unique_user_item_match_notification
        UNIQUE (user_id, item_id, matched_item_id)
);
