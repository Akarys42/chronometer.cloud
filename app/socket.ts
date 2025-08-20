const MAX_RETRIES = 10;

export interface Callbacks {
    onConnected(socket: ChronoSocket): void;

    onDisconnected(socket: ChronoSocket): void;

    onLost(socket: ChronoSocket): void;

    onMessage(event: MessageEvent): void;
}

export class ChronoSocket {
    private socket: WebSocket | null = null;
    private firstConnection: boolean = true;
    private attempts: number = MAX_RETRIES;

    constructor(
        public readonly url: string,
        private readonly callbacks: Callbacks,
    ) {
    }

    public get isFirstConnection(): boolean {
        return this.firstConnection;
    }

    public connect(): void {
        this.socket = new WebSocket(this.url);
        this.socket.onopen = () => {
            this.attempts = MAX_RETRIES;
            this.callbacks.onConnected(this);
            this.firstConnection = false;
        };
        this.socket.onclose = (event) => {
            this.socket = null;

            if (event.code === 1000) {
                // Normal closure
                return;
            }

            if (this.attempts-- > 0) {
                this.callbacks.onDisconnected(this);
                setTimeout(() => {
                    this.connect();
                }, 1.1 ** (MAX_RETRIES - this.attempts) * 1000); // Exponential backoff
            } else {
                this.callbacks.onLost(this);
            }
        };
        this.socket.onmessage = this.callbacks.onMessage;
    }

    public close(): void {
        if (this.socket !== null) {
            this.socket.close(1000);
        }
    }
}
