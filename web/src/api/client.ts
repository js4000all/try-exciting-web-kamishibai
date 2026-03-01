import type { ChapterScenarioResponse } from "./generated/models/ChapterScenarioResponse";
import type { ProjectDetailResponse } from "./generated/models/ProjectDetailResponse";
import type { ProjectListResponse } from "./generated/models/ProjectListResponse";
import type { SaveDataV0 } from "./generated/models/SaveDataV0";
import type { SaveReadResponse } from "./generated/models/SaveReadResponse";
import type { SaveWriteResponse } from "./generated/models/SaveWriteResponse";
import { ApiError as GeneratedApiError } from "./generated/core/ApiError";
import { ProjectsService } from "./generated/services/ProjectsService";
import { SavesService } from "./generated/services/SavesService";
import { ScenarioService } from "./generated/services/ScenarioService";

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

function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== "object" || value === null || !("error" in value)) {
    return false;
  }

  const error = (value as { error: unknown }).error;
  return typeof error === "object" && error !== null && "code" in error && "message" in error;
}

function toApiError(error: unknown): ApiError {
  if (error instanceof GeneratedApiError) {
    const body = error.body;
    if (isErrorEnvelope(body)) {
      return new ApiError({
        status: error.status,
        code: body.error.code,
        message: body.error.message,
        detail: body.error.detail,
        requestId: body.error.request_id,
      });
    }

    return new ApiError({
      status: error.status,
      code: "HTTP_ERROR",
      message: `Request failed: ${error.status}`,
      detail: body,
      requestId: "",
    });
  }

  return new ApiError({
    status: 0,
    code: "NETWORK_ERROR",
    message: error instanceof Error ? error.message : "Unexpected network error",
    detail: error,
    requestId: "",
  });
}

export const apiClient = {
  getProjects: async () => {
    try {
      return await ProjectsService.getProjectsApiV0ProjectsGet();
    } catch (error) {
      throw toApiError(error);
    }
  },
  getProject: async (projectId: string) => {
    try {
      return await ProjectsService.getProjectApiV0ProjectsProjectIdGet(projectId);
    } catch (error) {
      throw toApiError(error);
    }
  },
  getChapterScenario: async (projectId: string, chapterId: string) => {
    try {
      return await ScenarioService.getChapterScenarioApiV0ProjectsProjectIdScenarioChaptersChapterIdGet(projectId, chapterId);
    } catch (error) {
      throw toApiError(error);
    }
  },
  save: async (projectId: string, slot: string, data: SaveDataV0) => {
    try {
      return await SavesService.putSaveApiV0ProjectsProjectIdSavesSlotPut(projectId, slot, data);
    } catch (error) {
      throw toApiError(error);
    }
  },
  load: async (projectId: string, slot: string) => {
    try {
      return await SavesService.getSaveApiV0ProjectsProjectIdSavesSlotGet(projectId, slot);
    } catch (error) {
      throw toApiError(error);
    }
  },
};

export type { ChapterScenarioResponse, ProjectDetailResponse, ProjectListResponse, SaveDataV0, SaveReadResponse, SaveWriteResponse };
