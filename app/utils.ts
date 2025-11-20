import {useToast} from "#imports";

function send_error_message(error_message: string): void {
    useToast().add({
        title: "Uh oh!",
        description: error_message,
        color: "error",
        icon: "i-lucide-alert-triangle",
    })
}

class HttpCodeNotOkError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "HttpCodeNotOkError";
    }
}

export async function check_status(promise: Promise<Response>, error_message: string, bypass_404: boolean = false): Promise<Response> {
    return promise.then(r => {
        if (!r.ok && !(bypass_404 && r.status === 404)) {
            send_error_message(error_message);
            throw new HttpCodeNotOkError(`HTTP error! status: ${r.status}`);
        }
        return r;
    }).catch(r => {
        if (!(r instanceof HttpCodeNotOkError)) {
            send_error_message(error_message);
        }
        throw r;
    })
}

export function get_origin(): string {
    if (import.meta.server) {
        return "server://"
    }

    return window.location.origin;
}

export function unique<T>(value: T, index: number, array: T[]): boolean {
    return array.indexOf(value) === index;
}

export function addWindowEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | AddEventListenerOptions
): void {
    if (import.meta.server) {
        return;
    }

    window.addEventListener(type, listener, options);
}
