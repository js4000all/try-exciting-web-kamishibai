import type { components } from "../types/schema";

const API_BASE = "/api/v0";

type ProjectListResponse = components["schemas"]["ProjectListResponse"];
type ProjectDetailResponse = components["schemas"]["ProjectDetailResponse"];
type ChapterScenarioResponse = components["schemas"]["ChapterScenarioResponse"];
type SaveDataV0 = components["schemas"]["SaveDataV0"];
type SaveReadResponse = components["schemas"]["SaveReadResponse"];
type SaveWriteResponse = components["schemas"]["SaveWriteResponse"];

type ErrorEnvelope = {
  error: {
    code: string;
    message: string;
    detail: unknown;
    request_id: string;
  };
};

export class ApiError extends Error {
  code: string;
  detail: unknown;
  requestId: string;
  status: number;

  constructor(params: { status: number; code: string; message: string; detail: unknown; requestId: string }) {
    super(params.message);
    this.name = "ApiError";
    this.code = params.code;
    this.detail = params.detail;
    this.requestId = params.requestId;
    this.status = params.status;
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const body = (await response.json()) as T | ErrorEnvelope;

  if (!response.ok) {
    if (isErrorEnvelope(body)) {
      throw new ApiError({
        status: response.status,
        code: body.error.code,
        message: body.error.message,
        detail: body.error.detail,
        requestId: body.error.request_id,
      });
    }
    throw new ApiError({
      status: response.status,
      code: "HTTP_ERROR",
      message: `Request failed: ${response.status}`,
      detail: body,
      requestId: "",
    });
  }

  return body as T;
}

function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== "object" || value === null || !("error" in value)) {
    return false;
  }

  const error = (value as { error: unknown }).error;
  return typeof error === "object" && error !== null && "code" in error && "message" in error;
}

export const apiClient = {
  getProjects: () => requestJson<ProjectListResponse>("/projects"),
  getProject: (projectId: string) => requestJson<ProjectDetailResponse>(`/projects/${projectId}`),
  getChapterScenario: (projectId: string, chapterId: string) =>
    requestJson<ChapterScenarioResponse>(`/projects/${projectId}/scenario/chapters/${chapterId}`),
  save: (projectId: string, slot: string, data: SaveDataV0) =>
    requestJson<SaveWriteResponse>(`/projects/${projectId}/saves/${slot}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  load: (projectId: string, slot: string) => requestJson<SaveReadResponse>(`/projects/${projectId}/saves/${slot}`),
};

export type { ChapterScenarioResponse, ProjectDetailResponse, ProjectListResponse, SaveDataV0, SaveReadResponse, SaveWriteResponse };
