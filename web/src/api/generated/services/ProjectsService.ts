/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectDetailResponse } from '../models/ProjectDetailResponse';
import type { ProjectListResponse } from '../models/ProjectListResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProjectsService {
    /**
     * Get Projects
     * @returns ProjectListResponse Successful Response
     * @throws ApiError
     */
    public static getProjectsApiV0ProjectsGet(): CancelablePromise<ProjectListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v0/projects',
        });
    }
    /**
     * Get Project
     * @param projectId
     * @returns ProjectDetailResponse Successful Response
     * @throws ApiError
     */
    public static getProjectApiV0ProjectsProjectIdGet(
        projectId: string,
    ): CancelablePromise<ProjectDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v0/projects/{project_id}',
            path: {
                'project_id': projectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
