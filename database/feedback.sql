USE finditplus;

CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    handover_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    comment VARCHAR(1000) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_feedback_handover
        FOREIGN KEY (handover_id) REFERENCES handovers(id),

    CONSTRAINT fk_feedback_user
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT chk_feedback_rating
        CHECK (rating BETWEEN 1 AND 5)
);
