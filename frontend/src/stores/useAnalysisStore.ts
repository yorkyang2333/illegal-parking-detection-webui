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

// 预设提示词
const GEMINI_PROMPT = `假如你是一名交警，我将上传一段模拟校园周边道路返校时的模拟监控视频，请对视频中的车辆进行违停检测分析。
为适应实际情况，此处我们考虑且仅考虑车辆占机动车道停车的违停情况。如视频中，车辆在该车道上只要超过5s不动即标记为违停（位置坐标需每秒至少移动10才算作移动；如有乘客上下车即无视上述规则，直接视作违停）。
你的输出需包含以下结构化内容：
1.视频有效性确认：说明是否具备分析条件（如清晰度、拍摄角度等）
2.违停检测结果：
若存在违停：标注车牌号码（含置信度百分比；如无法识别，则详细输出该车的特征信息）、说明判断依据（如果判断车辆未向前移动，需给出车辆每一帧所处的位置坐标，给出计算过程与结果后判断；如有上下客行为，额外加以说明）
若未发现违停：说明判定依据（如车辆完全停在划线车位内）
3.技术说明：
车道线识别算法依据（颜色/虚实线类型判断）
车辆停留时长计算逻辑（连续静止时间）
特殊情况备注（如施工占道/故障车等非主观违停情形）
本视频中，右上角的数字为计时器，格式为[分]:[秒].[毫秒]，供计算时间间隔用；绿幕（如有）遮挡的是位于两旁合法停车格内的汽车。
请确保仅按照以上给出的规则进行判定，不要主观臆断，擅自修改规则。`

const QVQ_PROMPT = `请观看这段视频，输出且仅输出其中识别到车辆的车牌号。`

function getQwenPrompt(geminiResult: string, qvqResult: string): string {
    return `现有一段违停的分析报告：
${geminiResult}
由QVQ-Max重新识别了车牌号为：
${qvqResult}
请帮我把QVQ-Max识别到的车牌号替换报告中原先识别到的车牌号，依据且仅依据原报告中的内容，重新生成一份详尽违停报告。请依次输出：
1.违停车辆车牌号
2.该车辆违停原因（根据原分析报告中的内容进一步总结得出）
3.建议处罚（根据现行《中华人民共和国道路交通安全法》）
请确保仅按照原报告中的内容进行重新输出，保证格式清晰明确，逻辑性强，不要主观臆断。`
}

export const useAnalysisStore = defineStore('analysis', () => {
    // State
    const currentStep = ref(1)
    const videoFile = ref<File | null>(null)
    const videoPreviewUrl = ref<string | null>(null)
    const isProcessing = ref(false)
    const currentStreamingContent = ref('')

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
            title: '违停检测',
            description: '分析视频中的违停情况',
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
    const geminiResult = computed(() => steps.value[1]!.result)
    const qvqResult = computed(() => steps.value[2]!.result)
    const finalResult = computed(() => steps.value[3]!.result)
    const hasVideo = computed(() => videoFile.value !== null)
    const isAllCompleted = computed(() => steps.value.every(s => s.status === 'completed'))
    const currentStepInfo = computed(() => steps.value[currentStep.value - 1])

    // SSE for Gemini
    const geminiSSE = useSSE('/api/analyze/gemini', {
        onMessage: (data) => {
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

    // SSE for Qwen
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
            // Gemini 完成，自动执行 QVQ
            startQVQAnalysis()
        } else if (stepIndex === 2) {
            // QVQ 完成，自动执行 Qwen 合并
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
    }

    async function startAnalysis() {
        if (!videoFile.value) return

        isProcessing.value = true
        currentStep.value = 2
        currentStreamingContent.value = ''

        // 重置步骤 2-4 的状态
        for (let i = 1; i < 4; i++) {
            const step = steps.value[i]
            if (step) {
                step.status = 'pending'
                step.result = ''
                step.error = undefined
            }
        }

        // 开始 Gemini 分析
        steps.value[1]!.status = 'running'

        const formData = new FormData()
        formData.append('video', videoFile.value)
        formData.append('prompt', GEMINI_PROMPT)

        try {
            await geminiSSE.start({ video: videoFile.value.name, prompt: GEMINI_PROMPT, model: 'gemini' })
        } catch (err: any) {
            handleSSEError(err, 1)
        }
    }

    async function startQVQAnalysis() {
        currentStreamingContent.value = ''
        steps.value[2]!.status = 'running'

        try {
            await qvqSSE.start({ video: videoFile.value?.name, prompt: QVQ_PROMPT, model: 'qvq' })
        } catch (err: any) {
            handleSSEError(err, 2)
        }
    }

    async function startMergeAnalysis() {
        currentStreamingContent.value = ''
        steps.value[3]!.status = 'running'

        const prompt = getQwenPrompt(geminiResult.value, qvqResult.value)

        try {
            await qwenSSE.start({ prompt, model: 'qwen' })
        } catch (err: any) {
            handleSSEError(err, 3)
        }
    }

    function stopAnalysis() {
        geminiSSE.stop()
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
        geminiResult,
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
