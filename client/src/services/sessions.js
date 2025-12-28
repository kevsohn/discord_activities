export class SessionController {
    constructor({ discordSdk, auth }) {
        this.discordSdk = discordSdk;
        this.auth = auth;
        this.heartbeat_timer = null;
    }

    async create_session() {
        if (!this.auth?.user?.id) {
            throw new Error("Auth not ready");
        }

        const r = await fetch("/api/session/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: this.auth.session_id,
                user_id: this.auth.user.id,
            }),
        });

		if (!r.ok) {
			throw new Error('Failed to create session');
		}
    }

	start_heartbeat(interval_ms = 20_000) {  // 20 secs
        if (this.heartbeat_timer) return;

        this.heartbeat_timer = setInterval(() => {
            fetch("/api/session/heartbeat", {
                method: "POST",
                credentials: "include",
            }).catch(() => {
                // silent: TTL handles failure
            });
        }, interval_ms);
    }

    async start() {
		await this.create_session();
        this.start_heartbeat();
    }
}

