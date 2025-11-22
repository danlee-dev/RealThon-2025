// IndexedDB utilities for storing interview recordings

const DB_NAME = 'InterviewDB';
const STORE_NAME = 'recordings';
const DB_VERSION = 1;

/**
 * Opens the IndexedDB database
 */
function openDatabase(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => {
            reject(new Error('Failed to open IndexedDB'));
        };

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;

            // Create object store if it doesn't exist
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME);
            }
        };
    });
}

/**
 * Saves a video blob to IndexedDB
 * @param blob - The video blob to save
 * @param key - The key to store the video under (default: 'interview-video')
 */
export async function saveVideoToIndexedDB(blob: Blob, key: string = 'interview-video'): Promise<void> {
    try {
        const db = await openDatabase();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.put(blob, key);

            request.onsuccess = () => {
                console.log('[IndexedDB] Video saved successfully');
                resolve();
            };

            request.onerror = () => {
                reject(new Error('Failed to save video to IndexedDB'));
            };

            transaction.oncomplete = () => {
                db.close();
            };
        });
    } catch (error) {
        console.error('[IndexedDB] Error saving video:', error);
        throw error;
    }
}

/**
 * Retrieves a video blob from IndexedDB
 * @param key - The key of the video to retrieve (default: 'interview-video')
 * @returns The video blob or null if not found
 */
export async function getVideoFromIndexedDB(key: string = 'interview-video'): Promise<Blob | null> {
    try {
        const db = await openDatabase();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_NAME], 'readonly');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.get(key);

            request.onsuccess = () => {
                const result = request.result;
                if (result instanceof Blob) {
                    console.log('[IndexedDB] Video retrieved successfully');
                    resolve(result);
                } else {
                    console.log('[IndexedDB] No video found');
                    resolve(null);
                }
            };

            request.onerror = () => {
                reject(new Error('Failed to retrieve video from IndexedDB'));
            };

            transaction.oncomplete = () => {
                db.close();
            };
        });
    } catch (error) {
        console.error('[IndexedDB] Error retrieving video:', error);
        throw error;
    }
}

/**
 * Deletes a video from IndexedDB
 * @param key - The key of the video to delete (default: 'interview-video')
 */
export async function deleteVideoFromIndexedDB(key: string = 'interview-video'): Promise<void> {
    try {
        const db = await openDatabase();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.delete(key);

            request.onsuccess = () => {
                console.log('[IndexedDB] Video deleted successfully');
                resolve();
            };

            request.onerror = () => {
                reject(new Error('Failed to delete video from IndexedDB'));
            };

            transaction.oncomplete = () => {
                db.close();
            };
        });
    } catch (error) {
        console.error('[IndexedDB] Error deleting video:', error);
        throw error;
    }
}
