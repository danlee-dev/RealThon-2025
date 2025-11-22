'use client';

import React, { useRef, useState } from 'react';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    accept?: string;
    maxSize?: number; // in bytes
    error?: string;
}

export default function FileUpload({
    onFileSelect,
    accept = 'application/pdf',
    maxSize = 10 * 1024 * 1024, // 10MB default
    error,
}: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [fileName, setFileName] = useState<string>('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFile = (file: File) => {
        // Validate file type
        if (accept && !file.type.includes(accept.split('/')[1])) {
            alert(`파일 형식이 올바르지 않습니다. ${accept} 파일만 업로드 가능합니다.`);
            return;
        }

        // Validate file size
        if (maxSize && file.size > maxSize) {
            alert(`파일 크기가 너무 큽니다. 최대 ${(maxSize / 1024 / 1024).toFixed(0)}MB까지 업로드 가능합니다.`);
            return;
        }

        setFileName(file.name);
        onFileSelect(file);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="w-full">
            <div
                className={`
          relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer
          transition-all duration-300
          ${isDragging ? 'border-primary bg-primary/5 scale-105' : 'border-border hover:border-primary hover:bg-surface'}
          ${error ? 'border-error' : ''}
        `}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept={accept}
                    onChange={handleFileInput}
                    className="hidden"
                />

                <div className="flex flex-col items-center gap-4">
                    <svg
                        className={`w-16 h-16 ${isDragging ? 'text-primary scale-110' : 'text-text-secondary'} transition-all`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>

                    {fileName ? (
                        <div>
                            <p className="text-text font-semibold">{fileName}</p>
                            <p className="text-sm text-text-secondary mt-1">파일이 선택되었습니다</p>
                        </div>
                    ) : (
                        <div>
                            <p className="text-text font-semibold">
                                클릭하거나 파일을 드래그하여 업로드
                            </p>
                            <p className="text-sm text-text-secondary mt-1">
                                PDF 파일만 업로드 가능 (최대 {(maxSize / 1024 / 1024).toFixed(0)}MB)
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </div>
    );
}
