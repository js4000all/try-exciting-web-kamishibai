/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SaveDataV0 } from '../models/SaveDataV0';
import type { SaveReadResponse } from '../models/SaveReadResponse';
import type { SaveWriteResponse } from '../models/SaveWriteResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SavesService {
    /**
     * Put Save
     * @param projectId
     * @param slot
     * @param requestBody
     * @returns SaveWriteResponse Successful Response
     * @throws ApiError
     */
    public static putSaveApiV0ProjectsProjectIdSavesSlotPut(
        projectId: string,
        slot: string,
        requestBody: SaveDataV0,
    ): CancelablePromise<SaveWriteResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v0/projects/{project_id}/saves/{slot}',
            path: {
                'project_id': projectId,
                'slot': slot,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Save
     * @param projectId
     * @param slot
     * @returns SaveReadResponse Successful Response
     * @throws ApiError
     */
    public static getSaveApiV0ProjectsProjectIdSavesSlotGet(
        projectId: string,
        slot: string,
    ): CancelablePromise<SaveReadResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v0/projects/{project_id}/saves/{slot}',
            path: {
                'project_id': projectId,
                'slot': slot,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
