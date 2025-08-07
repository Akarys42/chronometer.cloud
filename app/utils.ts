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

export async function check_status(promise: Promise<Response>, error_message: string): Promise<Response> {
    return promise.then(r => {
        if (!r.ok) {
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
