/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChapterScenarioResponse } from '../models/ChapterScenarioResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ScenarioService {
    /**
     * Get Chapter Scenario
     * @param projectId
     * @param chapterId
     * @returns ChapterScenarioResponse Successful Response
     * @throws ApiError
     */
    public static getChapterScenarioApiV0ProjectsProjectIdScenarioChaptersChapterIdGet(
        projectId: string,
        chapterId: string,
    ): CancelablePromise<ChapterScenarioResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v0/projects/{project_id}/scenario/chapters/{chapter_id}',
            path: {
                'project_id': projectId,
                'chapter_id': chapterId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
