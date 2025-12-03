using Unity.Barracuda;
using UnityEngine;




public class Predict : MonoBehaviour
{
    //###### VARS
    [SerializeField]
    public NNModel modelAsset;

    private Model m_RuntimeModel;
    private IWorker m_Worker;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        m_RuntimeModel = ModelLoader.Load(modelAsset);
        m_Worker = WorkerFactory.CreateWorker(WorkerFactory.Type.CSharpBurst, m_RuntimeModel);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
