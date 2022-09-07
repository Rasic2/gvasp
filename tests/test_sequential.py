from common.task import SequentialTask

if __name__ == '__main__':
    task = SequentialTask(end='dos')
    task.generate(low=True, analysis=True)
