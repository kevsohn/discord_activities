export default class SessionManager {
    constructor(auth) {
        this.auth = auth;
        this.heartbeatTimer = null;
    }

    async createSession() {
        if (!this.auth?.user?.id) {
            throw new Error("Auth not ready");
        }

        const r = await fetch("/api/session/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: this.auth.user.id,
            }),
        });

		if (!r.ok) {
			throw new Error('Failed to create session');
		}
    }

	startHeartbeat(interval_ms = 30_000) {  // 20 secs
        if (this.heartbeatTimer) return;

        this.heartbeatTimer = setInterval(() => {
            fetch("/api/session/heartbeat", {
                method: "POST",
                credentials: "include",  // send cookie for session_id
            }).catch(() => {
                // silent: TTL handles failure
            });
        }, interval_ms);
    }

    async start() {
		await this.createSession();
        this.startHeartbeat();
    }
}

