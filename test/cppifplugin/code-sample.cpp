/*
 * プラグインで生成したいコードを、ハンドコーディングしてみた
 */ 

#if 0
signature sTask {
	ER		activate(void);
//	ER_UINT	cancelActivate(void);
//	ER		terminate(void);
//	ER		changePriority([in] PRI priority);
//	ER		getPriority([out] PRI *p_priority);
//	ER		refer([out] T_RTSK *pk_taskStatus);

//	ER		wakeup(void);
//	ER_UINT cancelWakeup(void);
//	ER		releaseWait(void);
	ER		suspend(void);
	ER		resume(void);
//	ER		raiseException([in] TEXPTN pattern);
};
#endif

#include "tTask_tecsgen.h"

tTask_CB tTask_CB_tab[2];

/* cell tTask Cell */
#define TaskCell  (&tTask_CB_tab[0])

/* signature sTask */
class sTask {
    virtual ER      activate() =0;
    virtual	ER		suspend() =0;
    virtual	ER		resume() =0;
};

/* celltype tTask */
class tTask {
    /* class for entry sTask eTask */
    class eTask_ : sTask {
        public : 
        /* constructor: internal use only */
        eTask_( tTask_IDX idx_);
        /* destructor */
        // ~eTask_();   unnecessary

        /* sTask functions */
        ER activate();
        ER suspend();
        ER resume();

        private:
        tTask_IDX idx;
    };

    /*--------  begin public ----------*/
    public:
    /* constructor */
    tTask( tTask_IDX idx );
    /* destructor */
    // ~tTask();   unnecessary

    /* entry sTask eTask */
    eTask_ eTask; 
    /*--------  end public ----------*/
};

/*-------------- begin: implementation (I/F code only) ----------------*/
/* constructor  */
inline    tTask::tTask(tTask_IDX idx): eTask(idx){ }

/* constructor: internal use only */
inline    tTask::eTask_::eTask_( tTask_IDX idx_) : idx(idx_){}

/* entry eTask functions */
inline ER tTask::eTask_::activate(){ return tTask_eTask_activate( idx ); }
inline ER tTask::eTask_::suspend(){ return tTask_eTask_suspend( idx ); }
inline ER tTask::eTask_::resume(){ return tTask_eTask_resume( idx ); }

/*-------------- end: implementation (I/F code only) ----------------*/

tTask  Task(TaskCell);

int main( int nargv, char **argv )
{

    Task.eTask.activate(); 
    Task.eTask.suspend(); 
    Task.eTask.resume(); 
}
