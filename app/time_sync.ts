type TimeSample = {
	t1: number;
	t2: number;
	t3: number;
	t4: number;
};

export class TimeSync {
	private ws: WebSocket;
	private samples: number[] = [];
	private pendingResolve?: (offset: number) => void;
	private readonly targetSamples: number;
	private isReady = false;

	constructor(private url: string, sampleCount = 10) {
		this.targetSamples = sampleCount;
		this.ws = new WebSocket(url);

		this.ws.onmessage = (event) => this.handleMessage(event);
	}

	/** Perform an async synchronization — resolves when enough samples are ready */
	public async synchronize(): Promise<number> {
		if (this.isReady) {
			// already synced
			return this.getAverageOffset();
		}

		return new Promise<number>((resolve) => {
			this.pendingResolve = resolve;
			this.startSampling();
		});
	}

	/** Internal: send a batch of sync pings */
	private startSampling() {
		// Wait until websocket is open
		if (this.ws.readyState !== WebSocket.OPEN) {
			this.ws.onopen = () => this.startSampling();
			return;
		}

		for (let i = 0; i < this.targetSamples; i++) {
			setTimeout(() => {
				const t1 = Date.now();
				this.ws.send(JSON.stringify({ t1 }));
			}, i * 200); // 200ms apart
		}
	}

	/** Internal: handle each response from the server */
	private handleMessage(event: MessageEvent) {
		const t4 = Date.now();
		const { t1, t2, t3 } = JSON.parse(event.data) as TimeSample;

		const offset = ((t2 - t1) + (t3 - t4)) / 2;
		const delay = (t4 - t1) - (t3 - t2);

		// Filter out high-delay samples to improve accuracy
		if (delay < 500) {
			this.samples.push(offset);
		}

		if (this.samples.length >= this.targetSamples && !this.isReady) {
			this.isReady = true;
			const avgOffset = this.getAverageOffset();
			this.pendingResolve?.(avgOffset);
		}
	}

	/** Get average offset (positive means server is ahead) */
	private getAverageOffset(): number {
		return this.samples.reduce((a, b) => a + b, 0) / this.samples.length;
	}

	/** Return server time based on current offset */
	public getServerTime(): Date {
		const avgOffset = this.getAverageOffset();
		return new Date(Date.now() + avgOffset);
	}
}
