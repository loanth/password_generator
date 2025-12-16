-- =========================
-- EXTENSION UUID
-- =========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================
-- TABLE USER
-- =========================
CREATE TABLE app_user (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    mail VARCHAR(255) UNIQUE NOT NULL,
    mdp_hash TEXT NOT NULL
);

-- =========================
-- TABLE GROUPE
-- =========================
CREATE TABLE groupe (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    admin_uuid UUID NOT NULL,

    CONSTRAINT fk_groupe_admin
        FOREIGN KEY (admin_uuid)
        REFERENCES app_user(uuid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLE PASSWORD
-- =========================
CREATE TABLE password (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    valeur_chiffree TEXT NOT NULL,
    intitule VARCHAR(150) NOT NULL
);

-- =========================
-- TABLE USER <-> GROUPE
-- =========================
CREATE TABLE membre (
    user_uuid UUID NOT NULL,
    groupe_id INT NOT NULL,

    PRIMARY KEY (user_uuid, groupe_id),

    CONSTRAINT fk_membre_user
        FOREIGN KEY (user_uuid)
        REFERENCES app_user(uuid)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_membre_groupe
        FOREIGN KEY (groupe_id)
        REFERENCES groupe(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLE USER <-> PASSWORD
-- =========================
CREATE TABLE user_pwd (
    user_uuid UUID NOT NULL,
    password_uuid UUID NOT NULL,

    PRIMARY KEY (user_uuid, password_uuid),

    CONSTRAINT fk_user_pwd_user
        FOREIGN KEY (user_uuid)
        REFERENCES app_user(uuid)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_user_pwd_password
        FOREIGN KEY (password_uuid)
        REFERENCES password(uuid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =========================
-- TABLE GROUPE <-> PASSWORD
-- =========================
CREATE TABLE grp_pwd (
    groupe_id INT NOT NULL,
    password_uuid UUID NOT NULL,

    PRIMARY KEY (groupe_id, password_uuid),

    CONSTRAINT fk_grp_pwd_groupe
        FOREIGN KEY (groupe_id)
        REFERENCES groupe(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_grp_pwd_password
        FOREIGN KEY (password_uuid)
        REFERENCES password(uuid)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
