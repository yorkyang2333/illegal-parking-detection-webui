import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSSE } from '@/composables/useSSE'
import { useAuthStore } from './useAuthStore'
import router from '@/router'

// 步骤状态类型
export type StepStatus = 'pending' | 'running' | 'completed' | 'error'

// 步骤信息
export interface Step {
    id: number
    title: string
    description: string
    status: StepStatus
    result: string
    error?: string
}

export const useAnalysisStore = defineStore('analysis', () => {
    // State
    const currentStep = ref(1)
    const videoFile = ref<File | null>(null)
    const videoPreviewUrl = ref<string | null>(null)
    const isProcessing = ref(false)
    const currentStreamingContent = ref('')
    const sam3Data = ref<any>(null)
    const uploadedFilename = ref<string>('')

    // 各步骤信息
    const steps = ref<Step[]>([
        {
            id: 1,
            title: '上传视频',
            description: '请上传需要分析的监控视频文件',
            status: 'pending',
            result: ''
        },
        {
            id: 2,
            title: '车辆追踪',
            description: 'SAM 3 分割追踪视频中的车辆并判定违停',
            status: 'pending',
            result: ''
        },
        {
            id: 3,
            title: '车牌识别',
            description: '识别违停车辆的车牌号',
            status: 'pending',
            result: ''
        },
        {
            id: 4,
            title: '报告生成',
            description: '合并分析结果，生成最终报告',
            status: 'pending',
            result: ''
        }
    ])

    // Computed
    const sam3Result = computed(() => steps.value[1]!.result)
    const qvqResult = computed(() => steps.value[2]!.result)
    const finalResult = computed(() => steps.value[3]!.result)
    const hasVideo = computed(() => videoFile.value !== null)
    const isAllCompleted = computed(() => steps.value.every(s => s.status === 'completed'))
    const currentStepInfo = computed(() => steps.value[currentStep.value - 1])

    // SSE for SAM 3
    const sam3SSE = useSSE('/api/analyze/sam3', {
        onMessage: (data) => {
            if (data.sam3_data) {
                sam3Data.value = data.sam3_data
            }
            if (data.status) {
                steps.value[1]!.result = data.text || ''
                return
            }
            const text = data.output?.choices?.[0]?.message?.content?.[0]?.text
            if (text) {
                currentStreamingContent.value += text
                steps.value[1]!.result = currentStreamingContent.value
            }
        },
        onError: (err: any) => {
            handleSSEError(err, 1)
        },
        onComplete: () => {
            handleStepComplete(1)
        }
    })

    // SSE for QVQ
    const qvqSSE = useSSE('/api/analyze/qvq', {
        onMessage: (data) => {
            if (data.status) {
                steps.value[2]!.result = data.text || ''
                return
            }
            const text = data.output?.choices?.[0]?.message?.content?.[0]?.text
            if (text) {
                currentStreamingContent.value += text
                steps.value[2]!.result = currentStreamingContent.value
            }
        },
        onError: (err: any) => {
            handleSSEError(err, 2)
        },
        onComplete: () => {
            handleStepComplete(2)
        }
    })

    // SSE for Qwen merge
    const qwenSSE = useSSE('/api/analyze/merge', {
        onMessage: (data) => {
            const text = data.output?.choices?.[0]?.message?.content?.[0]?.text
            if (text) {
                currentStreamingContent.value += text
                steps.value[3]!.result = currentStreamingContent.value
            }
        },
        onError: (err: any) => {
            handleSSEError(err, 3)
        },
        onComplete: () => {
            handleStepComplete(3)
        }
    })

    function handleSSEError(err: any, stepIndex: number) {
        if (err.status === 401) {
            const authStore = useAuthStore()
            authStore.clearError()
            router.push('/login')
        }
        const step = steps.value[stepIndex]
        if (step) {
            step.status = 'error'
            step.error = err.message || '处理失败'
        }
        isProcessing.value = false
    }

    function handleStepComplete(stepIndex: number) {
        const step = steps.value[stepIndex]
        if (step) {
            step.status = 'completed'
        }
        currentStep.value = stepIndex + 2 // 移动到下一步

        // 自动执行下一步
        if (stepIndex === 1) {
            // SAM 3 完成，自动执行 QVQ 车牌识别
            startQVQAnalysis()
        } else if (stepIndex === 2) {
            // QVQ 完成，自动执行 Qwen 合并报告
            startMergeAnalysis()
        } else if (stepIndex === 3) {
            // 全部完成
            isProcessing.value = false
        }
    }

    // Actions
    function setVideoFile(file: File) {
        videoFile.value = file
        if (videoPreviewUrl.value) {
            URL.revokeObjectURL(videoPreviewUrl.value)
        }
        videoPreviewUrl.value = URL.createObjectURL(file)
        steps.value[0]!.status = 'completed'
        steps.value[0]!.result = `已上传: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`
    }

    function clearVideoFile() {
        videoFile.value = null
        if (videoPreviewUrl.value) {
            URL.revokeObjectURL(videoPreviewUrl.value)
            videoPreviewUrl.value = null
        }
        steps.value[0]!.status = 'pending'
        steps.value[0]!.result = ''
        uploadedFilename.value = ''
    }

    async function uploadVideo(): Promise<boolean> {
        if (!videoFile.value) return false
        const formData = new FormData()
        formData.append('video', videoFile.value)
        try {
            const resp = await fetch('/api/upload-media', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            })
            if (!resp.ok) return false
            const data = await resp.json()
            uploadedFilename.value = data.filename
            return true
        } catch {
            return false
        }
    }

    async function startAnalysis() {
        if (!videoFile.value) return

        isProcessing.value = true
        currentStep.value = 2
        currentStreamingContent.value = ''
        sam3Data.value = null

        // 重置步骤 2-4 的状态
        for (let i = 1; i < 4; i++) {
            const step = steps.value[i]
            if (step) {
                step.status = 'pending'
                step.result = ''
                step.error = undefined
            }
        }

        // 先上传视频到后端
        if (!uploadedFilename.value) {
            const uploaded = await uploadVideo()
            if (!uploaded) {
                steps.value[1]!.status = 'error'
                steps.value[1]!.error = '视频上传失败'
                isProcessing.value = false
                return
            }
        }

        // 开始 SAM 3 分析
        steps.value[1]!.status = 'running'

        try {
            await sam3SSE.start({ video: uploadedFilename.value })
        } catch (err: any) {
            handleSSEError(err, 1)
        }
    }

    async function startQVQAnalysis() {
        currentStreamingContent.value = ''
        steps.value[2]!.status = 'running'

        try {
            await qvqSSE.start({
                video: uploadedFilename.value,
                sam3_results: sam3Data.value
            })
        } catch (err: any) {
            handleSSEError(err, 2)
        }
    }

    async function startMergeAnalysis() {
        currentStreamingContent.value = ''
        steps.value[3]!.status = 'running'

        try {
            await qwenSSE.start({
                sam3_result: sam3Result.value,
                qvq_result: qvqResult.value
            })
        } catch (err: any) {
            handleSSEError(err, 3)
        }
    }

    function stopAnalysis() {
        sam3SSE.stop()
        qvqSSE.stop()
        qwenSSE.stop()
        isProcessing.value = false

        // 将当前运行中的步骤标记为 pending
        steps.value.forEach(step => {
            if (step.status === 'running') {
                step.status = 'pending'
            }
        })
    }

    function resetAnalysis() {
        stopAnalysis()
        currentStep.value = 1
        currentStreamingContent.value = ''
        sam3Data.value = null

        // 重置所有步骤状态
        steps.value.forEach((step, index) => {
            if (index > 0) {
                step.status = 'pending'
                step.result = ''
                step.error = undefined
            }
        })
    }

    function goToStep(stepId: number) {
        // 只允许跳转到已完成的步骤或当前步骤
        if (stepId <= currentStep.value && !isProcessing.value) {
            currentStep.value = stepId
        }
    }

    return {
        // State
        currentStep,
        videoFile,
        videoPreviewUrl,
        isProcessing,
        steps,
        // Computed
        sam3Result,
        qvqResult,
        finalResult,
        hasVideo,
        isAllCompleted,
        currentStepInfo,
        // Actions
        setVideoFile,
        clearVideoFile,
        startAnalysis,
        stopAnalysis,
        resetAnalysis,
        goToStep
    }
})
